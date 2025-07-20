import sys
import io
import logging
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

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Console Handler (INFO and above)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(levelname)s: %(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# File Handler (DEBUG and above)
file_handler = logging.FileHandler('c_cleaner.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


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
        logger.error(f"Error: {e}")
        sys.exit(1)

    if sys.platform != "win32":
        logger.error("This tool is designed for Windows only.")
        sys.exit(1)

    # --- 2. Path Processing ---
    scan_path = normalize_path(args.path)
    validate_scan_path(scan_path)
    logger.info(f"Starting scan on {scan_path} for files > {args.min_size}...")

    # --- 3. Exclusion Processing ---
    base_system_exclusions = get_excluded_dirs(scan_path)
    user_exclusions = get_user_exclusions(args.exclude, CONFIG_FILENAME)
    excluded_dirs, validated_user_exclusions = process_exclusions(
        base_system_exclusions, user_exclusions
    )

    logger.info(
        f"Excluding {len(excluded_dirs)} total directories (system defaults + user-defined).")
    if validated_user_exclusions:
        logger.info("Active user-defined exclusions:")
        for path in sorted(list(validated_user_exclusions)):
            logger.info(f"  - {path}")

    # --- 4. File Scanning ---
    large_files = scan_large_files(scan_path, min_size_bytes, excluded_dirs)
    # The scanning progress line is a special case, keep print for now or refactor with rich.progress
    # print(" " * 100 + "\r", end="")  # Clear the "Scanning..." line

    # --- 5. Display Results ---
    large_files.sort(key=lambda x: x[1], reverse=True)
    files_to_show = large_files[:args.top]
    display_results(files_to_show, len(large_files))

    # --- 6. Interactive Deletion ---
    if files_to_show:
        interactive_delete(files_to_show)

    logger.info("\n操作完成。")


if __name__ == '__main__':
    main()
