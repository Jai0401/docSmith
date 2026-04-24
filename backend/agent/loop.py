"""Main agent loop for docSmith.

Uses direct git reading (no tool calls) to gather context, then a single LLM call to generate.
Simple and reliable - avoids tool-call loops.
"""
import os
import json
import re
from typing import Callable, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from .prompts import SYSTEM_PROMPT, DOCS_GENERATION_PROMPT, DOCKERFILE_PROMPT, DOCKER_COMPOSE_PROMPT
from .tools import bash, read_file, glob, grep, write_file
from ..services.git_service import get_repo_files
from ..services.openrouter_service import get_llm
from ..db import append_agent_log


async def _stream(callback: Callable, etype: str, content: str, extra: Optional[dict] = None):
    payload = {"type": etype, "content": content}
    if extra:
        payload.update(extra)
    await callback(json.dumps(payload))


async def generate_docs_agent(
    repo_url: str,
    generation_type: str,
    db_id: int,
    progress_callback: Callable,
    repo_dir: str,
) -> str:
    """
    Agent entry point — pipeline calls this after cloning and cleans up after.
    Simple approach: read all context → one LLM call → save result.
    Returns the generated content string.
    """
    output_path = os.path.join(repo_dir, "OUTPUT.md")

    if not os.getenv("OPENROUTER_API_KEY"):
        await _stream(progress_callback, "error", "OPENROUTER_API_KEY not set")
        append_agent_log(db_id, {"phase": "generate", "error": "Missing OPENROUTER_API_KEY"})
        return ""

    # --- Explore: read all project files directly ---
    await _stream(progress_callback, "thinking", "Exploring project structure...")
    append_agent_log(db_id, {"phase": "explore", "message": "Starting exploration"})

    patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx", "**/*.json",
                "**/*.md", "**/*.yaml", "**/*.yml", "**/*.toml", "**/*.go",
                "**/*.java", "**/*.rs", "**/*.cpp", "**/*.c", "**/*.h", "**/*.sh",
                "**/requirements.txt", "**/setup.py", "**/Makefile", "**/Dockerfile*",
                "**/.env*", "**/README*", "**/LICENSE*"]
    found_files = get_repo_files(repo_dir, patterns)

    key_names = {
        "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "venv",
        "README.md", "README.txt", "CONTRIBUTING.md", "LICENSE", "LICENSE.txt",
        "Makefile", "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        ".env", ".env.example", ".gitignore", "tsconfig.json", "webpack.config.js",
        "go.mod", "go.sum", "Cargo.toml", "pom.xml", "build.gradle",
        "vite.config.ts", "next.config.js", "vue.config.js"
    }
    key_files = [f for f in found_files if os.path.basename(f) in key_names or f.endswith('.md')]

    # Read all key files
    file_contents = {}
    for f in key_files[:30]:
        try:
            full_path = os.path.join(repo_dir, f)
            with open(full_path, "r", encoding="utf-8", errors="ignore") as fh:
                content = fh.read()[:5000]  # limit per file
                file_contents[f] = content
        except Exception:
            pass

    await _stream(progress_callback, "reading", f"Read {len(file_contents)} key files...")
    append_agent_log(db_id, {"phase": "explore", "files_found": len(found_files), "key_files": list(file_contents.keys())})

    # Build context string
    context_parts = []
    try:
        root_files = os.listdir(repo_dir)
        context_parts.append(f"## Root directory: {root_files}\n")
    except Exception:
        pass

    for fname, content in file_contents.items():
        context_parts.append(f"\n## File: {fname}\n```\n{content}\n```\n")

    full_context = "\n".join(context_parts)

    # --- Generate ---
    await _stream(progress_callback, "generating", f"Generating {generation_type}...")
    append_agent_log(db_id, {"phase": "generate", "message": "Starting generation"})

    if generation_type == "dockerfile":
        gen_prompt = DOCKERFILE_PROMPT.format(repo_path=repo_dir)
    elif generation_type == "docker-compose":
        gen_prompt = DOCKER_COMPOSE_PROMPT.format(repo_path=repo_dir)
    else:
        gen_prompt = DOCS_GENERATION_PROMPT.format(repo_path=repo_dir)

    system_msg = SYSTEM_PROMPT.format(generation_type=generation_type, output_path=output_path)
    user_msg = (
        f"{gen_prompt}\n\n"
        f"### Project Files\n{full_context[:20000]}\n\n"
        f"Now generate the {generation_type} for this project. "
        f"IMPORTANT: Write the final output to: {output_path}\n"
        f"First reason about the project, then use the write_file tool to save your output."
    )

    llm = get_llm()

    from langchain_core.tools import tool as lc_tool

    # Create tools as simple callables
    @lc_tool
    def write_file_tool(path: str, content: str) -> str:
        """Write content to a file. Use this to save your generated output."""
        if not path.startswith("/tmp/docsmith_repos"):
            return f"Error: Access denied. Path must be within /tmp/docsmith_repos"
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote {len(content)} chars to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    @lc_tool
    def glob_tool(pattern: str) -> str:
        """Find files matching a glob pattern."""
        base = "/tmp/docsmith_repos"
        results = []
        for root, dirs, files in os.walk(base):
            for name in files:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, base)
                import fnmatch
                if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(name, pattern):
                    results.append(rel_path)
        return json.dumps(results[:100], indent=2)

    @lc_tool
    def read_file_tool(path: str) -> str:
        """Read a file."""
        if not path.startswith("/tmp/docsmith_repos"):
            return f"Error: Access denied"
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()[:3000]
        except Exception as e:
            return f"Error: {e}"

    @lc_tool
    def bash_tool(command: str) -> str:
        """Run a bash command."""
        import subprocess
        try:
            r = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd="/tmp")
            return r.stdout + r.stderr
        except Exception as e:
            return f"Error: {e}"

    TOOLS = [write_file_tool, glob_tool, read_file_tool, bash_tool]
    TOOL_MAP = {t.name: t for t in TOOLS}

    llm_with_tools = llm.bind_tools(TOOLS)

    messages = [[SystemMessage(content=system_msg), HumanMessage(content=user_msg)]]

    MAX_TURNS = 5
    for turn in range(MAX_TURNS):
        response = await llm_with_tools.agenerate(messages)
        ai_text = response.generations[0][0].text
        ai_msg = response.generations[0][0].message
        tool_calls = ai_msg.tool_calls if hasattr(ai_msg, 'tool_calls') else []

        # Add AI message to conversation
        from langchain_core.messages import AIMessage
        messages.append([AIMessage(content=ai_text)])

        if tool_calls:
            for tc in tool_calls:
                name = tc.get('name', '')
                raw_args = tc.get('args', {})
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except:
                        args = {"raw": raw_args}
                else:
                    args = raw_args

                # Normalize args: LLM often uses 'input' but tool expects its actual param name
                normalized_args = args.copy()
                
                # Special handling for bash tool: 'input' -> 'command'
                if name == "bash_tool" and "input" in normalized_args:
                    normalized_args["command"] = normalized_args.pop("input")
                # Handle read_file, glob, grep, write_file similarly
                elif name == "read_file_tool" and "input" in normalized_args:
                    normalized_args["path"] = normalized_args.pop("input")
                elif name == "glob_tool" and "input" in normalized_args:
                    normalized_args["pattern"] = normalized_args.pop("input")
                elif name == "grep_tool" and "input" in normalized_args:
                    # grep has regex and file_pattern
                    if "regex" not in normalized_args:
                        normalized_args["regex"] = normalized_args.pop("input")
                elif name == "write_file_tool" and "input" in normalized_args:
                    # write_file has path and content separately; input might be the content
                    if "content" not in normalized_args:
                        normalized_args["content"] = normalized_args.pop("input")
                
                if name in TOOL_MAP:
                    try:
                        result = str(TOOL_MAP[name].invoke(normalized_args))[:500]
                        append_agent_log(db_id, {"tool": name, "input": str(args)[:100], "output": result[:200]})
                        await _stream(progress_callback, "tool", f"Ran {name}", {"result": result[:200]})
                        messages.append([AIMessage(content=f"[{name} result: {result}]")])
                    except Exception as e:
                        messages.append([AIMessage(content=f"[{name} error: {str(e)}]")])
                else:
                    messages.append([AIMessage(content=f"[Unknown tool: {name}]")])
        else:
            # No tool calls - check if output file was written
            break

    # Try to read the output file
    try:
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                final = f.read()
            if final and len(final) > 100:
                await _stream(progress_callback, "done", f"Generated {len(final)} chars")
                append_agent_log(db_id, {"phase": "complete", "output_size": len(final)})
                return final
    except Exception:
        pass

    # Fallback: save the raw content
    final = ai_text if ai_text else ""
    if final:
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final)
            await _stream(progress_callback, "done", f"Saved {len(final)} chars (fallback)")
            append_agent_log(db_id, {"phase": "complete", "output_size": len(final), "fallback": True})
            return final
        except Exception:
            pass

    append_agent_log(db_id, {"phase": "error", "error": "No content generated"})
    return final
