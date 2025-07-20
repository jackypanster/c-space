import os
import stat
import shutil
import logging
from pathlib import Path
from typing import List, Tuple, Set

from utils import FILE_ATTRIBUTE_HIDDEN, FILE_ATTRIBUTE_SYSTEM

logger = logging.getLogger(__name__)


def get_excluded_dirs(scan_path: Path) -> Set[str]:
    """
    Gets a set of normalized, lowercase, absolute paths for directories to be excluded.
    """
    env_vars = [
        'windir', 'ProgramFiles', 'ProgramFiles(x88)',
        'ProgramData', 'APPDATA', 'LOCALAPPDATA'
    ]
    excluded_dirs = set()
    for var in env_vars:
        path_str = os.environ.get(var)
        if path_str:
            excluded_dirs.add(str(Path(path_str).resolve()).lower())

    drive_root = scan_path.drive + "\\"
    for d in ['$Recycle.Bin', 'System Volume Information', 'Config.Msi', 'Recovery']:
        excluded_dirs.add(str(Path(drive_root) / d).lower())

    return excluded_dirs


def _is_dir_excluded(dir_path: Path, excluded_paths: Set[str]) -> bool:
    """
    Helper to check if a directory should be skipped.
    Logs warnings for inaccessible directories.
    """
    if dir_path.name.startswith('.'):
        return True

    if str(dir_path).lower() in excluded_paths:
        return True

    try:
        # Check for Windows 'hidden' attribute
        if dir_path.stat().st_file_attributes & FILE_ATTRIBUTE_HIDDEN:
            return True
    except PermissionError:
        logger.warning(f"Permission denied to access directory '{dir_path}', skipping.")
        return True
    except FileNotFoundError:
        logger.warning(f"Directory '{dir_path}' not found, skipping.")
        return True
    except OSError as e:
        logger.warning(f"OS error accessing directory '{dir_path}': {e}, skipping.")
        return True

    return False


def scan_large_files(root_dir: Path, min_size_bytes: int, excluded_dirs: Set[str]) -> List[Tuple[str, int]]:
    """
    Scans a directory for large files, applying all exclusion rules.
    Logs scanning progress and errors.
    """
    large_files = []
    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80

    for root, dirs, files in os.walk(root_dir, topdown=True):
        current_root = Path(root)
        display_root = str(current_root)
        if len(display_root) > terminal_width - 12:
            display_root = "..." + display_root[-(terminal_width - 15):]
        
        # Log scanning progress at DEBUG level, print to console for immediate feedback
        logger.debug(f"Scanning: {current_root}")
        print(f"Scanning: {display_root.ljust(terminal_width - 10)}\r", end="", flush=True)

        # Prune directories in-place for efficiency
        dirs[:] = [d for d in dirs if not _is_dir_excluded(
            current_root / d, excluded_dirs)]

        for filename in files:
            if filename.startswith('.'):
                continue

            try:
                file_path = current_root / filename
                stats = file_path.stat()

                if stats.st_file_attributes & (FILE_ATTRIBUTE_HIDDEN | FILE_ATTRIBUTE_SYSTEM):
                    logger.debug(f"Skipping hidden/system file: '{file_path}'")
                    continue

                if stats.st_size >= min_size_bytes:
                    large_files.append((str(file_path), stats.st_size))
            except PermissionError:
                logger.warning(f"Permission denied to access file '{file_path}', skipping.")
                continue
            except FileNotFoundError:
                logger.warning(f"File '{file_path}' not found, skipping.")
                continue
            except OSError as e:
                logger.warning(f"OS error accessing file '{file_path}': {e}, skipping.")
                continue

    return large_files
