import sys
from pathlib import Path


def normalize_path(path_str: str) -> Path:
    """
    Normalizes a path string and returns a pathlib.Path object.
    - Handles MSYS/Git Bash paths (e.g., /d/folder) on Windows.
    - Resolves to an absolute path.
    """
    # On Windows, a path starting with a single slash like /d/foo is a Git Bash/MSYS path.
    if sys.platform == "win32" and path_str.startswith('/') and not path_str.startswith('//'):
        parts = path_str.split('/')
        if len(parts) > 1 and len(parts[1]) == 1 and parts[1].isalpha():
            drive = parts[1].upper()
            path_str = f"{drive}:/{'/'.join(parts[2:])}"

    # Let pathlib handle the rest of the normalization and resolution.
    return Path(path_str).resolve()


def validate_scan_path(path: Path):
    """Validates the scan path, exiting if it's not a valid directory."""
    if not path.is_dir():
        print(
            f"Error: The specified path '{path}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)
