"""Git operations service."""
import os
import shutil
from git import Repo


def clone_repo(repo_url: str, dest_path: str) -> bool:
    """Clone a git repo to dest_path. Returns True on success."""
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)
    try:
        Repo.clone_from(repo_url, dest_path, depth=1)
        return True
    except Exception:
        return False


def get_repo_files(repo_path: str, patterns: list[str]) -> list[str]:
    """Return files matching patterns in the repo."""
    import glob
    files = []
    for pat in patterns:
        full_pat = os.path.join(repo_path, pat)
        files.extend(glob.glob(full_pat, recursive=True))
    return files


def cleanup_repo(repo_path: str):
    """Remove the cloned repo directory."""
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)