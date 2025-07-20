import argparse
import sys
import shutil

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


def main():
    """
    Main function to orchestrate the file scanning and cleaning process.
    """
    parser = argparse.ArgumentParser(
        description="Scan C: drive for large files and offer to delete them safely.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--min-size', type=str, default='50MB',
                        help="Minimum file size (e.g., '100MB', '1GB').\nDefault: 50MB")
    parser.add_argument('--top', type=int, default=20,
                        help="Number of largest files to display.\nDefault: 20")
    args = parser.parse_args()

    try:
        min_size_bytes = parse_size(args.min_size)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if sys.platform != "win32":
        print("Error: This tool is designed for Windows only.", file=sys.stderr)
        sys.exit(1)

    scan_path = "C:\\"
    print(f"Starting scan on {scan_path} for files > {args.min_size}...")

    excluded_dirs = get_excluded_dirs(scan_path)
    print(f"Excluding {len(excluded_dirs)} key system/program directories.")

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
