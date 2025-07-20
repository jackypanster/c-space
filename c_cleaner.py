import argparse
import sys
import shutil
import os

from scanner import get_excluded_dirs, scan_large_files
from utils import parse_size, format_size
from deleter import interactive_delete


def display_results(files_to_display: list, total_found: int):
    """
    Displays the found files in a formatted table as per PRD.
    """
    print(f"\n发现超过指定大小的文件共 {total_found} 个。", end="")
    if not files_to_display:
        print()  # Newline
        return

    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80  # Fallback for environments without a tty

    top_n = len(files_to_display)
    print(f" 显示前 {top_n} 个：\n")

    # Calculate dynamic width for the path column
    header_fixed_width = 4 + 12  # Width for '#', '大小', and spacing
    path_width = terminal_width - header_fixed_width - 1

    # Header from PRD
    print(f"{'#':<4}{'大小':<12}{'文件路径'}")
    print(f"{'-'*4}{'-'*12}{'-' * (path_width if path_width > 10 else 64)}")

    # Table rows
    for i, (path, size) in enumerate(files_to_display, 1):
        formatted_size = format_size(size)
        display_path = path
        if len(path) > path_width and path_width > 15:
            half = (path_width - 3) // 2
            display_path = f"{path[:half]}...{path[-half:]}"
        print(f"{str(i)+'.':<4}{formatted_size:<12}{display_path}")


def _normalize_path(path_str: str) -> str:
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


def main():
    """
    Main function to orchestrate the file scanning and cleaning process.
    """
    parser = argparse.ArgumentParser(
        description="Scan a specified drive or path for large files and offer to delete them safely.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--min-size', type=str, default='50MB',
                        help="Minimum file size (e.g., '100MB', '1GB').\nDefault: 50MB")
    parser.add_argument('--top', type=int, default=20,
                        help="Number of largest files to display.\nDefault: 20")
    parser.add_argument(
        '--exclude',
        nargs='+',
        metavar='EXCLUDE_PATH',
        default=[],
        help="One or more additional directory paths to exclude from the scan.")
    parser.add_argument(
        'path',
        nargs='?',
        default='C:\\',
        help="Path to scan (e.g., 'D:\\', 'C:\\Users').\nDefault: C:\\"
    )
    args = parser.parse_args()

    try:
        min_size_bytes = parse_size(args.min_size)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if sys.platform != "win32":
        print("Error: This tool is designed for Windows only.", file=sys.stderr)
        sys.exit(1)

    # --- Path Processing ---
    scan_path = _normalize_path(args.path)
    if not os.path.isdir(scan_path):
        print(
            f"Error: The specified path '{scan_path}' does not exist or is not a directory.", file=sys.stderr)
        sys.exit(1)

    print(f"Starting scan on {scan_path} for files > {args.min_size}...")

    # --- Exclusion List Processing ---
    # 1. Get system default exclusions
    excluded_dirs = get_excluded_dirs(scan_path)

    # 2. Load exclusions from config file `.cleaner_ignore`
    config_file_path = '.cleaner_ignore'
    config_exclusions = set()
    if os.path.isfile(config_file_path):
        print(
            f"Found config file: '{config_file_path}', loading exclusions...")
        with open(config_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                path = line.strip()
                if path and not path.startswith('#'):
                    config_exclusions.add(path)

    # 3. Combine CLI and config exclusions and validate them
    all_user_paths = set(args.exclude) | config_exclusions
    validated_user_exclusions = set()
    for user_path in all_user_paths:
        normalized_user_path = _normalize_path(user_path)
        if os.path.isdir(normalized_user_path):
            excluded_dirs.add(os.path.normpath(normalized_user_path).lower())
            validated_user_exclusions.add(normalized_user_path)
        else:
            print(
                f"Warning: Exclude path '{user_path}' from config or CLI is not a valid directory, ignoring.", file=sys.stderr)

    print(
        f"Excluding {len(excluded_dirs)} total directories (system defaults + user-defined).")
    if validated_user_exclusions:
        print("Active user-defined exclusions:")
        for path in sorted(list(validated_user_exclusions)):
            print(f"  - {path}")

    large_files = scan_large_files(scan_path, min_size_bytes, excluded_dirs)

    # Clear the "Scanning..." line
    print(" " * 100 + "\r", end="")

    # --- Step 3: Sort, Format, and Display ---
    large_files.sort(key=lambda x: x[1], reverse=True)
    files_to_show = large_files[:args.top]
    display_results(files_to_show, len(large_files))

    # --- Step 4: Interactive Deletion ---
    if files_to_show:
        interactive_delete(files_to_show)

    print("\n操作完成。")


if __name__ == '__main__':
    main()
