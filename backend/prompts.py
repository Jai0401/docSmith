prompt_01 = """
You are an experienced technical documentation expert. Your task is to analyze the provided codebase and create **comprehensive, well-structured, and user-friendly documentation**. The output must be in **Markdown format**.  

### Codebase:  
{codebase}  

### Documentation Guidelines:  

Organize the documentation into the following sections. If a section is not applicable, omit it. Add any additional sections or subsections as necessary to enhance clarity and usability. Use **Markdown styling** to maintain a clear hierarchy with headings and subheadings:  

**Project Overview**
   - Purpose of the project
   - Key features
   - Supported platforms or requirements  

**Getting Started**
   - Installation or setup instructions
   - Dependencies or prerequisites  

**Usage**(only if applicable)
   - How to use the project in brief
   - Code snippets or examples(very minimal and brief)
   - Don't generate this section if not required  

**Code Structure**(only if applicable)
   - Folder and file organization
   - Brief descriptions of key components  

**API Documentation** (if applicable)
   - Endpoints (GET, POST, etc.)
   - Input and output formats  
   - Example API requests and responses  

**Contributing** (if applicable)
   - Contribution guidelines
   - Code style and best practices  

**FAQ** (if applicable)
   - Common issues and resolutions  

**License** (if applicable)
   - Licensing details  

### Additional Notes:
- Use appropriate Markdown headers (#, ##, ###, etc.) for section hierarchy.
- Ensure clarity by using lists, tables, or code blocks (`code`) where helpful.
- Whenever using code block The code sequence must end with '<end_code>' sequence.
- Keep the language simple and concise.
- Provide examples or explanations where needed to ensure comprehensibility for users of varying expertise.

---
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