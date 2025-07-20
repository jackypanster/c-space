import shutil
from typing import List, Tuple

from utils import format_size


def display_results(files_to_display: List[Tuple[str, int]], total_found: int):
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

    header_fixed_width = 4 + 12  # Width for '#', '大小', and spacing
    path_width = terminal_width - header_fixed_width - 1

    print(f"{'#':<4}{'大小':<12}{'文件路径'}")
    print(f"{'-'*4}{'-'*12}{'-' * (path_width if path_width > 10 else 64)}")

    for i, (path, size) in enumerate(files_to_display, 1):
        formatted_size = format_size(size)
        display_path = path
        if len(path) > path_width and path_width > 15:
            half = (path_width - 3) // 2
            display_path = f"{path[:half]}...{path[-half:]}"
        print(f"{str(i)+'.':<4}{formatted_size:<12}{display_path}")
