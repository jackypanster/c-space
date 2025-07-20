import os
import sys


def normalize_path(path_str: str) -> str:
    r"""
    Normalizes a path string, handling shell-specific formats for Windows.
    - Converts MSYS/Git Bash paths (e.g., /d/folder) to Windows paths (D:\folder).
    - Appends a trailing slash to root drives (e.g., C: -> C:\).
    - Returns an absolute path.
    """
    # 0. Normalize slashes for Windows consistency, especially for mixed-env inputs
    path_str = path_str.replace('/', '\\')

    # 1. Handle MSYS/Git Bash style paths
    if sys.platform == "win32" and path_str.startswith('\\'):
        parts = path_str.split('\\')
        if len(parts) > 1 and len(parts[1]) == 1 and parts[1].isalpha():
            # Correctly form an absolute path from the drive letter, e.g., 'D:\'
            drive = parts[1].upper() + ':\\'
            path_str = os.path.join(drive, *parts[2:])

    # 2. Handle root drive without slash
    if len(path_str) == 2 and path_str[1] == ':' and path_str[0].isalpha():
        path_str += os.path.sep

    return os.path.abspath(path_str)


def validate_scan_path(path: str):
    """Validates the scan path, exiting if it's not a valid directory."""
    if not os.path.isdir(path):
        print(
            f"Error: The specified path '{path}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)
