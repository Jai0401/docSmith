"""LangChain tools for the docSmith agent."""
import os
import json
import glob as glob_module
from typing import Callable, Optional
from langchain_core.tools import tool


class AgentLogger:
    """Helper to collect agent actions into a list."""

    def __init__(self, db_id: int, append_fn: Callable):
        self.db_id = db_id
        self.append_fn = append_fn
        self.actions = []

    def log(self, tool_name: str, input_data: dict, output: str = ""):
        entry = {
            "tool": tool_name,
            "input": input_data,
            "output": output[:500] if output and len(output) > 500 else output,
        }
        self.actions.append(entry)
        self.append_fn(self.db_id, entry)


@tool
def bash(command: str) -> str:
    """Execute a shell command and return stdout/stderr."""
    import subprocess
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            cwd="/tmp",
        )
        output = result.stdout + result.stderr
        return output[:4000]  # truncate very long output
    except subprocess.TimeoutExpired:
        return "Command timed out after 120 seconds"
    except Exception as e:
        return f"Error: {str(e)}"


@tool
def read_file(path: str) -> str:
    """Read and return the contents of a file."""
    # Security: restrict to the repo directory
    if not path.startswith("/tmp/docsmith_repos"):
        return f"Error: Access denied. Path must be within /tmp/docsmith_repos"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="latin-1") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


@tool
def glob(pattern: str) -> str:
    """Find files matching a glob pattern in the repo directory."""
    # Use /tmp/docsmith_repos as root
    base = "/tmp/docsmith_repos"
    results = []
    for root, dirs, files in os.walk(base):
        for name in files:
            full_path = os.path.join(root, name)
            rel_path = os.path.relpath(full_path, base)
            if glob_module.fnmatch.fnmatch(rel_path, pattern) or glob_module.fnmatch.fnmatch(name, pattern):
                results.append(rel_path)
    if not results:
        return f"No files found matching: {pattern}"
    return json.dumps(results[:200], indent=2)  # limit to 200 files


@tool
def grep(pattern: str, file_pattern: str = "*") -> str:
    """Search for pattern in files matching file_pattern."""
    base = "/tmp/docsmith_repos"
    matches = []
    for root, dirs, files in os.walk(base):
        for name in files:
            if not glob_module.fnmatch.fnmatch(name, file_pattern):
                continue
            full_path = os.path.join(root, name)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if pattern in line:
                            rel = os.path.relpath(full_path, base)
                            matches.append(f"{rel}:{i}: {line.rstrip()}")
            except Exception:
                continue
    if not matches:
        return f"No matches found for '{pattern}' in files matching '{file_pattern}'"
    return json.dumps(matches[:100], indent=2)


@tool
def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path."""
    # Security: restrict to the repo directory
    if not path.startswith("/tmp/docsmith_repos"):
        return f"Error: Access denied. Path must be within /tmp/docsmith_repos"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {e}"