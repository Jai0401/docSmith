"""docSmith FastAPI application."""
import os
import asyncio
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

from . import db
from .agent.loop import generate_docs_agent
from .services.git_service import clone_repo, cleanup_repo

# Ensure DB is initialized
db.init_db()

# In-memory event queues for SSE streams
sse_queues: dict[int, asyncio.Queue] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clean up SSE queues on shutdown."""
    yield
    sse_queues.clear()


app = FastAPI(title="docSmith API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    url: str
    generation_type: str = "docs"


class RegenerateRequest(BaseModel):
    url: str


@app.get("/ping")
async def ping():
    return {"status": "ok", "version": "1.0.0"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    """Start a new generation job."""
    if req.generation_type not in ("docs", "dockerfile", "docker-compose"):
        raise HTTPException(status_code=400, detail="generation_type must be docs, dockerfile, or docker-compose")

    try:
        gen_id = db.create_generation(req.url, req.generation_type)
    except Exception:
        # UNIQUE constraint — reuse existing record
        for g in db.list_generations():
            if g["repo_url"] == req.url:
                gen_id = g["id"]
                db.update_status(gen_id, "pending")
                break
        else:
            raise HTTPException(status_code=500, detail="Failed to create generation record")

    sse_queues[gen_id] = asyncio.Queue()
    asyncio.create_task(_run_agent(gen_id, req.url, req.generation_type))

    return {"id": gen_id, "status": "pending"}


@app.get("/stream/{gen_id}")
async def stream(gen_id: int):
    """SSE endpoint for agent progress events."""
    if gen_id not in sse_queues:
        gen = db.get_generation(gen_id)
        if not gen:
            raise HTTPException(status_code=404, detail="Generation not found")
        sse_queues[gen_id] = asyncio.Queue()
        if gen["status"] in ("done", "failed"):
            await sse_queues[gen_id].put(json.dumps({"type": gen["status"], "content": gen["content"] or "Completed"}))

    async def event_generator():
        queue = sse_queues[gen_id]
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=60)
                yield f"data: {event}\n\n"
                if '"type":"done"' in event or '"type":"error"' in event:
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type':'ping'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/result/{gen_id}")
async def result(gen_id: int):
    """Return the generated content for a job."""
    gen = db.get_generation(gen_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    return {
        "id": gen["id"],
        "repo_url": gen["repo_url"],
        "generation_type": gen["generation_type"],
        "status": gen["status"],
        "content": gen["content"],
        "agent_log": json.loads(gen["agent_log"]) if gen["agent_log"] else [],
        "created_at": gen["created_at"],
        "updated_at": gen["updated_at"],
    }


@app.post("/regenerate/{gen_id}")
async def regenerate(gen_id: int):
    """Re-run the agent for an existing record, overwriting it."""
    gen = db.get_generation(gen_id)
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")

    db.update_status(gen_id, "pending")
    db.update_content(gen_id, "", "pending")

    if gen_id not in sse_queues:
        sse_queues[gen_id] = asyncio.Queue()
    else:
        while not sse_queues[gen_id].empty():
            sse_queues[gen_id].get_nowait()

    asyncio.create_task(_run_agent(gen_id, gen["repo_url"], gen["generation_type"]))
    return {"id": gen_id, "status": "pending"}


@app.get("/history")
async def history():
    """List all generation records."""
    return db.list_generations()


async def _run_agent(gen_id: int, url: str, gen_type: str):
    """Pipeline: clone → agent → cleanup → save (deterministic steps)."""
    repo_dir = f"/tmp/docsmith_repos/{gen_id}"

    async def progress_callback(event_json: str):
        if gen_id in sse_queues:
            await sse_queues[gen_id].put(event_json)

    # Step 1: Clone
    db.update_status(gen_id, "running")
    await progress_callback(json.dumps({"type": "cloning", "content": f"Cloning {url}..."}))

    if not clone_repo(url, repo_dir):
        await progress_callback(json.dumps({"type": "error", "content": f"Failed to clone {url}"}))
        db.update_status(gen_id, "failed")
        return

    await progress_callback(json.dumps({"type": "cloned", "content": f"Repository cloned to {repo_dir}"}))

    final_content = ""
    try:
        # Step 2: Agent (explore → read → generate)
        final_content = await generate_docs_agent(url, gen_type, gen_id, progress_callback, repo_dir)
    except Exception as e:
        await progress_callback(json.dumps({"type": "error", "content": str(e)}))
        db.update_status(gen_id, "failed")
        return
    finally:
        # Step 3: Cleanup (deterministic — always runs)
        cleanup_repo(repo_dir)
        await progress_callback(json.dumps({"type": "cleaned", "content": "Repository cleaned up"}))

    # Step 4: Save to DB
    db.update_content(gen_id, final_content, "done")
    await progress_callback(json.dumps({"type": "done", "content": "Generation complete!", "result": final_content[:500]}))