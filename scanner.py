import os
import stat
import shutil
from typing import List, Tuple, Set

from utils import FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_SYSTEM


def get_excluded_dirs(root_drive: str) -> Set[str]:
    """
    Gets a set of normalized, absolute paths for directories to be excluded.
    """
    env_vars = [
        'windir', 'ProgramFiles', 'ProgramFiles(x86)',
        'ProgramData', 'APPDATA', 'LOCALAPPDATA'
    ]
    # Use a set comprehension with the walrus operator (:=) for conciseness
    excluded_dirs = {
        os.path.normpath(p).lower()
        for v in env_vars if (p := os.environ.get(v))
    }

    # Add other common system directories
    root_drive = os.path.normpath(root_drive)
    for d in ['$Recycle.Bin', 'System Volume Information', 'Config.Msi']:
        excluded_dirs.add(os.path.join(root_drive, d).lower())

    return excluded_dirs


def _is_dir_excluded(root: str, dirname: str, excluded_paths: Set[str]) -> bool:
    """Helper to check if a directory should be skipped."""
    if dirname.startswith('.'):
        return True

    dir_path = os.path.join(root, dirname)
    if dir_path.lower() in excluded_paths:
        return True

    try:
        # Check for Windows 'hidden' attribute
        if os.stat(dir_path).st_file_attributes & FILE_ATTRIBUTE_HIDDEN:
            return True
    except (PermissionError, FileNotFoundError, OSError):
        return True  # Treat inaccessible directories as excluded

    return False


def scan_large_files(root_dir: str, min_size_bytes: int, excluded_dirs: Set[str]) -> List[Tuple[str, int]]:
    """
    Scans a directory for large files, applying all exclusion rules.
    """
    large_files = []
    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80

    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Truncate the scanning path for display to fit the terminal
        display_root = root
        if len(display_root) > terminal_width - 12:
            display_root = "..." + display_root[-(terminal_width - 15):]
        print(
            f"Scanning: {display_root.ljust(terminal_width - 10)}\r", end="", flush=True)

        # Prune directories in-place for efficiency using the helper function
        dirs[:] = [d for d in dirs if not _is_dir_excluded(
            root, d, excluded_dirs)]

        for filename in files:
            if filename.startswith('.'):
                continue

            try:
                file_path = os.path.join(root, filename)
            s    stats = os.stat(file_path)

               if stats.st_file_attributes & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM):
                    continue

                if stats.st_size >= min_size_bytes:
                    large_files.append((file_path, stats.st_size))
            except (PermissionError, FileNotFoundError, OSError):
                continue

    return large_files
