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

@app.get("/ping")
async def ping():
    """
    A lightweight route to keep the server alive.
    """
    return {"message": "Pong!"}

# Updated template to generate structured JSON-like output
DOCUMENTATION_TEMPLATE = """
You are a technical documentation expert tasked with analyzing the following codebase and generating comprehensive and well-structured documentation. Please return the documentation in **Markdown format**.

### Codebase:
{codebase}

### Documentation Structure:

Ensure to organize the documentation into the following sections. If a section or sub-section is not applicable to the codebase, feel free to remove it. You can also add any additional relevant sections. Use appropriate Markdown styling and formatting to ensure clarity, use different font sizes to maintain clear hierarchy like main haeding(name of project) with #project-name and all sub sequent haeding under it with lower size ##,###.

---

#### 1. **Project Overview:**
- **Description**: Provide a detailed description of the project, including its background and context.
- **Purpose**: State the primary goals and objectives of the project.
- **Features**: List the key features and capabilities of the project.
- **Target Audience**: Define who the project is intended for (e.g., developers, businesses, end users).

#### 2. **Setup Instructions:**
- **Prerequisites**: List any software, tools, or libraries that must be installed before setting up the project.
- **Installation**: Provide step-by-step instructions for installing the project.
- **Configuration**: Detail any configuration settings or files that need to be modified.
- **Environment Setup**: Explain the environment setup (e.g., development, production, etc.).
- **First-Time Run**: Instructions on running the project for the first time, including any initial setup required.

#### 3. **Core Modules and Architecture:**
- **Components**: List the main components of the project (e.g., services, classes, modules).
- **Relationships**: Describe how the components interact with each other.
- **Key Functionalities**: Highlight the main functionalities each module/component offers.
- **Internal Architecture**: Provide details on the project's internal architecture (e.g., microservices, monolithic structure).

#### 4. **API Endpoints:**
- **Endpoints**: List and describe all available API endpoints.
- **Request/Response Formats**: Explain the structure of requests and responses.
- **Authentication**: Specify the authentication methods supported by the API.
- **Example Requests**: Provide example API requests for better understanding.
- **Error Handling**: Describe how errors are handled and what error messages to expect.

#### 5. **Usage Examples:**
- **Common Use Cases**: Outline typical scenarios for using the project.
- **Code Samples**: Provide relevant code snippets demonstrating how to use the project.
- **Best Practices**: List best practices for using the project efficiently and effectively.
- **Tips and Tricks**: Offer any tips, shortcuts, or helpful advice for users.

#### 6. **Dependencies:**
- **Required Libraries**: List all libraries or dependencies required to run the project.
- **Version Requirements**: Specify the version of each library or tool.
- **System Prerequisites**: Outline the system requirements (e.g., operating system, hardware).
- **External Services**: List any external services or APIs the project depends on.

#### 7. **Future Improvements and Roadmap:**
- **Enhancements**: Mention potential improvements or features that could be added in the future.
- **Optimization Opportunities**: Suggest areas of the project that could be optimized for better performance or efficiency.
- **Planned Features**: List the features that are planned for future releases.
- **Known Limitations**: Mention any limitations or known issues that users should be aware of.

---

Ensure that each section is formatted clearly using **Markdown syntax** and that all the values (such as descriptions, lists, and code snippets) are well-organized and easy to read.
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
