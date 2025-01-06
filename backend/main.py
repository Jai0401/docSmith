from typing import Union, Dict, Any
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, File, UploadFile, HTTPException,Body
from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
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
llm = GoogleGenerativeAI(
    model="gemini-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7,
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

        print(f"Packed codebase .txt file created at {packed_file_path}")

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
        # Run repomix with the remote URL to get the packed codebase as a .txt file
        packed_file = await run_repomix(repo_url.url)

        # Read the packed codebase file
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        # Process the content to generate documentation
        documentation = await process_large_codebase(codebase_content)

        return documentation

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Documentation generation failed: {str(e)}"
        )

    

# Updated template to generate structured JSON-like output
DOCUMENTATION_TEMPLATE = """
You are a technical documentation expert. Analyze this codebase and generate comprehensive documentation.
Return the documentation in a markdown format.

Codebase:
{codebase}

Generate documentation with this structure, providing each section as a dictionary with descriptive keys and detailed values, if some section or sub-section is not applicable, 
you can remove it and also add any additional sections if needed, make it suitable for github readme.md file, you can use appropriate styling and formatting.:

1. Overview:
- description: Detailed project description
- purpose: Main purpose of the project
- features: List of key features and capabilities
- audience: Target audience description

2. Setup Instructions:
- prerequisites: List of prerequisites
- installation: Step-by-step installation guide
- configuration: Configuration details
- environment: Environment setup instructions
- first_run: First-time run instructions

3. Core Modules:
- components: List of main components
- relationships: Component relationships
- functionalities: Key functionalities
- architecture: Internal architecture details

4. API Endpoints:
- endpoints: List of all endpoints
- formats: Request/response formats
- auth: Authentication methods
- examples: Example requests
- error_handling: Error handling details

5. Usage Examples:
- scenarios: Common use case scenarios
- code_samples: Example code snippets
- best_practices: Best practices list
- tips: Usage tips and tricks

6. Dependencies:
- libraries: Required libraries list
- versions: Version requirements
- system_requirements: System prerequisites
- services: Required external services

7. Future Improvements:
- enhancements: Potential enhancements
- optimization: Optimization opportunities
- planned_features: Planned features list
- limitations: Known limitations

Format each section ensure all values are properly formatted in markdown.
"""

# Create documentation pipeline using modern approach
documentation_prompt = PromptTemplate(
    input_variables=["codebase"],
    template=DOCUMENTATION_TEMPLATE
)

# Create chain using the pipe operator
documentation_chain = documentation_prompt | llm

def parse_documentation_response(content: str):
    """
    Parse the LLM response without enforcing type restrictions.
    """
    try:
        if not content.strip():
            raise ValueError("LLM response is empty.")

        # Attempt to parse the JSON response
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse JSON from LLM response: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error while parsing response: {str(e)}"
        )

def combine_documentation_chunks(chunks):
    """
    Combine multiple documentation chunks into a single coherent document.
    """
    return chunks[0] if chunks else {}

async def process_large_codebase(codebase: str, max_chunk_size: int = 30000):
    """
    Process large codebases without strict type constraints.
    """
    try:
        if len(codebase) <= max_chunk_size:
            print("Processing small codebase")
            raw_result = await documentation_chain.ainvoke({"codebase": codebase})
            logging.info(f"LLM raw response: {raw_result}")
            print(raw_result)
            # return parse_documentation_response(raw_result)
            return raw_result

        # Split and process codebase
        chunks = [codebase[i:i + max_chunk_size] for i in range(0, len(codebase), max_chunk_size)]
        all_docs = []
        for chunk in chunks:
            print("Processing codebase chunk")
            raw_result = await documentation_chain.ainvoke({"codebase": chunk})
            # print(raw_result)
            logging.info(f"Chunk raw response: {raw_result}")
            # all_docs.append(parse_documentation_response(raw_result))
            return raw_result
            # all_docs.append(raw_result)
            # print(all_docs[0])

        # return combine_documentation_chunks(all_docs)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Documentation generation failed: {str(e)}"
        )

@app.post("/generate-docs")
async def generate_documentation(file: UploadFile = File(...)):
    """
    Generate structured documentation from a codebase file.
    """
    try:
        if not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=400,
                detail="Please provide a .txt file"
            )

        content = await file.read()
        codebase_content = content.decode('utf-8')

        # Generate structured documentation
        print(codebase_content[:100])
        documentation = await process_large_codebase(codebase_content)

        return documentation

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Documentation generation failed: {str(e)}"
        )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
