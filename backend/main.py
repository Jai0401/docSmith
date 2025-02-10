from typing import Union, Dict, Any
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, File, UploadFile, HTTPException,Body
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .prompts import prompt_02, prompt_04, prompt_00, prompt_01, prompt_05
import re
import os
import json
import uvicorn
import logging
import subprocess

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Documentation Generator API",
    description="API for generating structured documentation from codebase using Gemini and Langchain",
    version="1.0.0"
)
# Allow CORS for all origins (you can change this if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

# Load environment variables and initialize Gemini
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    max_output_tokens=4096
)


# New API input model for GitHub URL
class RepoURL(BaseModel):
    url: HttpUrl

import tempfile

async def run_repomix(repo_url: str) -> str:
    """
    Run Repomix on a remote GitHub repository to generate a .txt file containing the codebase content.
    """
    try:
        # Convert the URL to a string
        repo_url = str(repo_url)

        # Create a temporary directory for the output file
        temp_dir = tempfile.mkdtemp()

        # Define the path for the output .txt file
        packed_file_path = os.path.join(temp_dir, "packed_codebase.txt")

        # Run Repomix on the remote GitHub repository to create the .txt file
        result = subprocess.run(
            [
                "repomix",
                "--remote", repo_url,
                "--output", packed_file_path
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            raise RuntimeError(f"Repomix failed: {result.stderr.decode()}")

        # print(f"Packed codebase .txt file created at {packed_file_path}")

        # Return the path to the packed .txt file
        return packed_file_path

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error during Repomix execution: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in processing remote repository: {str(e)}")


@app.post("/generate-docs-from-url")
async def generate_docs_from_url(repo_url: RepoURL):
    """
    Generate documentation directly from a remote GitHub repository.
    """
    try:
        # Convert to string and normalize URL (remove trailing slash)
        normalized_url = str(repo_url.url).rstrip("/")

        # Validate GitHub repository URL
        if not is_valid_github_url(normalized_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

        print(normalized_url)

        # Run repomix with the remote URL to get the packed codebase as a .txt file
        packed_file = await run_repomix(normalized_url)

        # Read the packed codebase file
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        # Use prompt_01 for Documentation generation
        dockerfile_prompt = PromptTemplate(
            input_variables=["codebase"],
            template=prompt_01
        )
        dockerfile_chain = dockerfile_prompt | llm
        
        result = await dockerfile_chain.ainvoke({"codebase": codebase_content})
        return result.content


    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Documentation generation failed: {str(e)}"
        )

@app.post("/generate-dockerfile")
async def generate_dockerfile(repo_url: RepoURL):
    """
    Generate Dockerfile from a remote GitHub repository.
    """
    try:
        normalized_url = str(repo_url.url).rstrip("/")
        if not is_valid_github_url(normalized_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

        packed_file = await run_repomix(normalized_url)
        
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        # Use prompt_04 for Dockerfile generation
        dockerfile_prompt = PromptTemplate(
            input_variables=["codebase"],
            template=prompt_04
        )
        dockerfile_chain = dockerfile_prompt | llm
        
        result = await dockerfile_chain.ainvoke({"codebase": codebase_content})
        return result.content

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dockerfile generation failed: {str(e)}"
        )

@app.post("/generate-docker-compose")
async def generate_docker_compose(repo_url: RepoURL):
    """
    Generate Docker Compose configuration from a remote GitHub repository.
    """
    try:
        normalized_url = str(repo_url.url).rstrip("/")
        if not is_valid_github_url(normalized_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

        packed_file = await run_repomix(normalized_url)
        
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        # Use prompt_05 for Docker Compose generation
        compose_prompt = PromptTemplate(
            input_variables=["codebase"],
            template=prompt_05
        )
        compose_chain = compose_prompt | llm
        
        result = await compose_chain.ainvoke({"codebase": codebase_content})
        return result.content

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Docker Compose generation failed: {str(e)}"
        )

@app.get("/ping")
async def ping():
    """
    A lightweight route to keep the server alive.
    """
    return {"message": "Pong!"}

def is_valid_github_url(url: str) -> bool:
    """Check if the URL is a valid GitHub repository link."""
    pattern = r"^https://github\.com/[\w-]+/[\w-]+/?$"
    return re.match(pattern, url) is not None



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
