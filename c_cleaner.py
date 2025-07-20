import sys
import io
from pathlib import Path

# New modular imports
from args import setup_parser
from path_handler import normalize_path, validate_scan_path
from exclusion_handler import get_user_exclusions, process_exclusions
from display import display_results

# Existing modular imports
from scanner import get_excluded_dirs, scan_large_files
from utils import parse_size, CONFIG_FILENAME
from deleter import interactive_delete


def main():
    """
    Main function to orchestrate the file scanning and cleaning process.
    """
    # --- 0. Configure Encoding for Windows ---
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # --- 1. Setup & Argument Parsing ---
    parser = setup_parser()
    args = parser.parse_args()

    try:
        min_size_bytes = parse_size(args.min_size)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if sys.platform != "win32":
        print("Error: This tool is designed for Windows only.", file=sys.stderr)
        sys.exit(1)

    # --- 2. Path Processing ---
    scan_path = normalize_path(args.path)
    validate_scan_path(scan_path)
    print(f"Starting scan on {scan_path} for files > {args.min_size}...")

    # --- 3. Exclusion Processing ---
    base_system_exclusions = get_excluded_dirs(scan_path)
    user_exclusions = get_user_exclusions(args.exclude, CONFIG_FILENAME)
    excluded_dirs, validated_user_exclusions = process_exclusions(
        base_system_exclusions, user_exclusions
    )

    print(
        f"Excluding {len(excluded_dirs)} total directories (system defaults + user-defined).")
    if validated_user_exclusions:
        print("Active user-defined exclusions:")
        for path in sorted(list(validated_user_exclusions)):
            print(f"  - {path}")

    # --- 4. File Scanning ---
    large_files = scan_large_files(scan_path, min_size_bytes, excluded_dirs)
    print(" " * 100 + "\r", end="")  # Clear the "Scanning..." line

    # --- 5. Display Results ---
    large_files.sort(key=lambda x: x[1], reverse=True)
    files_to_show = large_files[:args.top]
    display_results(files_to_show, len(large_files))

    # --- 6. Interactive Deletion ---
    if files_to_show:
        interactive_delete(files_to_show)

    print("\n操作完成。")


if __name__ == '__main__':
    main()
