import argparse


def setup_parser() -> argparse.ArgumentParser:
    """Sets up and returns the command-line argument parser."""
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
    return parser
