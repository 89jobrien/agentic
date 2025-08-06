import tomli
import re
from pathlib import Path
from typing import List, Iterable


def read_ignore_file(repo_path: Path) -> List[str]:
    """
    Reads patterns from an .agenticignore file in the given directory.
    
    Args:
        repo_path: The path to the repository root directory.

    Returns:
        A list of glob patterns to ignore.
    """
    ignore_file = repo_path / ".agenticignore"
    if not ignore_file.is_file():
        return []

    patterns = []
    with open(ignore_file, "r") as f:
        for line in f:
            stripped_line = line.strip()
            # Ignore comments and empty lines
            if stripped_line and not stripped_line.startswith("#"):
                patterns.append(stripped_line)
    return patterns

def get_project_name(start_dir: Path) -> str:
    """
    Recursively searches upwards from a starting directory to find a
    pyproject.toml file and extract the project name.

    If no file or name is found, it falls back to the original directory's name.

    Args:
        start_dir: The directory to start the search from.

    Returns:
        The project name as a string.
    """
    current_dir = start_dir.resolve()
    # Search upwards from the current directory to the filesystem root
    while current_dir != current_dir.parent:
        pyproject_path = current_dir / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with open(pyproject_path, "rb") as f:
                    data = tomli.load(f)
                # Safely get the project name from the parsed data
                project_name = data.get("project", {}).get("name")
                if project_name:
                    return project_name
            except Exception:
                # If parsing fails for any reason, break and use fallback
                break
        current_dir = current_dir.parent

    # Fallback to the original directory name if not found or on error
    return start_dir.name


def get_files_in_dir(dir_path: Path) -> Iterable[Path]:
    for entry in dir_path.iterdir():
        if entry.is_file():
            yield entry


def get_subdirs(dir_path: Path) -> Iterable[Path]:
    for entry in dir_path.iterdir():
        if entry.is_dir():
            yield entry
