prompt_00 = """
You are a technical documentation expert. Your task is to analyze the provided codebase and generate a concise, well-structured GitHub README in Markdown format. Follow these guidelines:

codebase: {codebase}

Output Requirements:

Markdown Format Only: Use proper Markdown headers (e.g., #, ##, ###) for section hierarchy.
Avoid Unnecessary Code Blocks: Only use code blocks for actual code snippets or configuration examples. Regular text should not be wrapped in code blocks.
Conciseness: Keep each section clear and concise. Avoid overly lengthy sections or unnecessary details.
Documentation Sections:
Include only sections that are relevant to the codebase. If a section is not applicable, omit it. Organize your output into the following sections:

a. Project Overview:

Description: Provide a brief background, context, and summary of what the project does.
Purpose: Clearly state the primary goals and objectives.
Key Features: List the main features or capabilities.
Target Audience: Define who the project is intended for (e.g., developers, businesses, end users).
b. Setup Instructions:

Prerequisites: List required software, tools, or libraries.
Installation: Provide step-by-step installation instructions.
Configuration: Explain any configuration settings or file modifications needed.
First-Time Run: Include instructions for running the project initially.
c. Core Modules and Architecture:

Components: List and briefly describe the main components (e.g., services, classes, modules).
Relationships: Explain how these components interact.
Key Functionalities: Summarize the main functionalities offered by each component.
d. API Endpoints (if applicable):

Endpoint List: Document all available API endpoints.
Request/Response Formats: Describe the structure of requests and responses.
Authentication: Specify supported authentication methods.
Example Requests: Provide concise examples to illustrate usage.
Error Handling: Outline how errors are managed and what messages users might encounter.
e. Usage Examples:

Common Use Cases: Highlight typical scenarios for using the project.
Best Practices: List any recommended practices for effective usage.
Tips: Offer useful hints or shortcuts where relevant.
f. Dependencies:

Libraries and Tools: List required libraries or dependencies along with version requirements.
System Prerequisites: Mention any operating system or hardware requirements.
External Services: Identify any external APIs or services the project relies on.
g. Future Improvements and Roadmap:

Planned Enhancements: Outline features or improvements planned for future releases.
Optimization Opportunities: Suggest areas that could be optimized.
Known Limitations: Mention any limitations or issues users should be aware of.
General Guidelines:

Relevance: Only include sections that apply to the codebase. Omit or condense sections that are not relevant.
Clarity and Readability: Ensure the documentation is accessible for users with various levels of expertise.
GitHub Best Practices: Follow common GitHub README conventions—keep the structure logical and the language straightforward.
By following these instructions, your output should be a ready-to-use GitHub README that adheres to best practices for technical documentation and prompt engineering, tailored for use with Gemini LLM.
"""


prompt_01 = """
You are an experienced technical documentation expert. Your task is to analyze the provided codebase and create **comprehensive, well-structured, and user-friendly documentation**. The output must be in **Markdown format**.  

### Codebase:  
{codebase}  

### Documentation Guidelines:  

Organize the documentation into the following sections. If a section is not applicable, omit it. Add any additional sections or subsections as necessary to enhance clarity and usability. Use **Markdown styling** to maintain a clear hierarchy with headings and subheadings:  

1. **Project Overview**
   - Purpose of the project
   - Key features
   - Supported platforms or requirements  

2. **Getting Started**
   - Installation or setup instructions
   - Dependencies or prerequisites  

3. **Usage**
   - How to use the project
   - Code snippets or examples  

4. **Code Structure**
   - Folder and file organization
   - Brief descriptions of key components  

5. **API Documentation** (if applicable)
   - Endpoints (GET, POST, etc.)
   - Input and output formats  
   - Example API requests and responses  

6. **Contributing** (if applicable)
   - Contribution guidelines
   - Code style and best practices  

7. **FAQ** (if applicable)
   - Common issues and resolutions  

8. **License** (if applicable)
   - Licensing details  

### Additional Notes:
- Use appropriate Markdown headers (#, ##, ###, etc.) for section hierarchy.
- Ensure clarity by using lists, tables, or code blocks (`code`) where helpful.
- Keep the language simple and concise.
- Provide examples or explanations where needed to ensure comprehensibility for users of varying expertise.

---
"""

prompt_02 = """
You are an experienced technical documentation expert with strong reasoning skills. Your task is to thoroughly analyze the provided codebase, identify its core functionalities and structure, and then produce comprehensive, well-organized, and user-friendly documentation in Markdown format.

**Process Overview:**

1. **Analyze the Codebase:**
   - Examine the provided code carefully.
   - Identify the project's purpose, key features, and any unique components.
   - Note the overall structure and any patterns that influence documentation (e.g., folder organization, API endpoints, etc.).

2. **Plan Your Documentation:**
   - Map the findings to relevant documentation sections.
   - Decide which sections apply based on your analysis and omit any that are not relevant.
   - Ensure the final structure is logical and accessible to users with varying levels of expertise.

3. **Generate the Final Output:**
   - Create a clear, hierarchically organized Markdown document.
   - Use headings, subheadings, lists, tables, and inline code formatting as needed.
   - Verify that every important aspect of the codebase is covered with clarity and consistency.

**Provided Codebase:**  
{codebase}

**Documentation Guidelines:**

1. **Project Overview**  
   - Purpose of the project  
   - Key features  
   - Supported platforms or requirements

2. **Getting Started**  
   - Installation or setup instructions  
   - Dependencies or prerequisites

3. **Usage**  
   - How to use the project  
   - Minimal and illustrative code snippets or examples

4. **Code Structure**  
   - Folder and file organization  
   - Brief descriptions of key components

5. **API Documentation** (if applicable)  
   - Endpoints (GET, POST, etc.)  
   - Input and output formats  
   - Example API requests and responses

6. **Contributing** (if applicable)  
   - Contribution guidelines  
   - Code style and best practices

7. **FAQ** (if applicable)  
   - Common issues and resolutions

8. **License** (if applicable)  
   - Licensing details

**Additional Notes:**

- Use appropriate Markdown headers (`#`, `##`, `###`, etc.) to clearly establish the hierarchy.
- Incorporate lists, tables, or inline code formatting (`code`) to enhance clarity where appropriate.
- Keep explanations straightforward and concise, ensuring the document is accessible to both beginners and experts.
- Avoid overly lengthy code blocks unless absolutely necessary for clarity.
- Before providing your final answer, internally review your analysis to confirm that all critical aspects of the codebase are documented accurately and completely.
- Do not include meta commentary or internal reasoning details in the final output.
"""


prompt_04 = """
You are an experienced Docker expert and DevOps engineer. Your task is to generate a **Dockerfile** for the provided project. Please analyze the project details below and create a Dockerfile that adheres to Docker best practices.

### Project Details:
{codebase}

### Dockerfile Requirements:
- Choose an appropriate base image that aligns with the project's technology stack.
- Install any necessary dependencies.
- Copy the project source code into the container.
- Expose any required ports.
- Define the command to run the application.
- Use multi-stage builds if applicable for optimization.
- Ensure the Dockerfile is production-ready and optimized.
- Use best practices for security and efficiency.

Provide the final output as a valid Dockerfile without any additional commentary.
"""

prompt_05 = """
You are an experienced Docker Compose expert and DevOps engineer. The entire codebase is provided below as a repomix generated file. Your task is to analyze the codebase to identify all necessary services, dependencies, and configurations, and then generate a complete and optimized **docker-compose** configuration.

### Provided Codebase (repomix generated file):
{codebase}

### docker-compose Generation Guidelines:
- Analyze the codebase to determine all required services (e.g., web server, databases, caching systems, etc.).
- For each service, specify the build context or Docker image as appropriate.
- Configure essential settings including ports, environment variables, volumes, and networks.
- Define any dependencies between services and ensure the correct startup order.
- Ensure the configuration adheres to docker-compose best practices and is compatible with version '3' or higher.
- Optimize the configuration for the intended environment (development or production).
- Use best practices for security and efficiency.

Provide the final output as a valid docker-compose configuration in YAML format without any additional commentary.
"""