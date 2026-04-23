# docSmith - Agentic Documentation Generator

A FastAPI-based backend that uses AI agents to automatically generate documentation, Dockerfiles, and docker-compose files from Git repositories.

## Tech Stack

- **Python 3.10+**
- **FastAPI** - Web framework
- **SQLite** - Database (built-in)
- **OpenRouter API** - LLM backend (free models with web search)
- **GitPython** - Git operations
- **LangChain** - Agent framework
- **SSE** - Server-Sent Events for real-time progress

## Project Structure

```
docsmith-rebuild/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── db.py                # SQLite setup & operations
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── tools.py         # LangChain tools (bash, read, glob, grep, write)
│   │   ├── loop.py          # Main agent loop
│   │   └── prompts.py       # System & generation prompts
│   └── services/
│       ├── __init__.py
│       ├── git_service.py   # Clone, file operations
│       └── openrouter_service.py  # OpenRouter LLM client
└── frontend-patch/
    └── README.md            # Frontend integration instructions
```

## Setup

### 1. Install Dependencies

```bash
pip install fastapi uvicorn langchain langchain-openai gitpython python-dotenv sse-starlette
```

### 2. Set Environment Variable

```bash
export OPENROUTER_API_KEY=your_openrouter_api_key_here
```

Get your free OpenRouter API key at: https://openrouter.ai/keys

### 3. Run the Server

```bash
cd backend
python main.py
```

Or with uvicorn:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
```
GET /ping
→ {"status": "ok", "version": "1.0.0"}
```

### Start Generation
```
POST /generate
Body: {"url": "https://github.com/user/repo", "generation_type": "docs"}
→ {"id": 1, "status": "pending"}
```

**generation_type** values: `docs`, `dockerfile`, `docker-compose`

### Stream Progress (SSE)
```
GET /stream/{id}
```
Events:
- `{"type": "cloning", "content": "Cloning..."}`
- `{"type": "thinking", "content": "Exploring..."}`
- `{"type": "reading", "content": "Reading..."}`
- `{"type": "generating", "content": "Generating..."}`
- `{"type": "done", "content": "...", "result": "..."}`
- `{"type": "error", "content": "..."}`

### Get Result
```
GET /result/{id}
→ {"id": 1, "repo_url": "...", "generation_type": "docs", "status": "done", "content": "...", ...}
```

### Regenerate
```
POST /regenerate/{id}
→ {"id": 1, "status": "pending"}
```

### History
```
GET /history
→ [{"id": 1, "repo_url": "...", "generation_type": "...", "status": "...", ...}, ...]
```

## Example Usage

```bash
# Start generation
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/facebook/react", "generation_type": "docs"}'

# Stream progress (SSE)
curl http://localhost:8000/stream/1

# Get result
curl http://localhost:8000/result/1

# List history
curl http://localhost:8000/history
```

## Agent Tools

The agent has access to these tools:

| Tool | Description |
|------|-------------|
| `bash` | Execute shell commands |
| `read_file` | Read file contents |
| `glob` | Find files matching pattern |
| `grep` | Search for text in files |
| `write_file` | Write content to file |

## Workflow

1. **Clone** - Repository is cloned to `/tmp/docsmith_repos/{id}/`
2. **Explore** - Agent glob finds key files, reads configs
3. **Generate** - LLM generates docs using repo context
4. **Save** - Output saved to repo directory as `OUTPUT.md`

## Database

SQLite at `/tmp/docsmith.db`:

```sql
CREATE TABLE generations (
    id INTEGER PRIMARY KEY,
    repo_url TEXT UNIQUE,
    generation_type TEXT,
    content TEXT,
    status TEXT DEFAULT 'pending',
    agent_log TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Frontend Integration

See `frontend-patch/README.md` for React integration instructions.
