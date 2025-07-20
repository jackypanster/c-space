from typing import List, Tuple

from rich.console import Console
from rich.table import Table

from utils import format_size


def display_results(files_to_display: List[Tuple[str, int]], total_found: int):
    """
    Displays the found files in a formatted table using rich.
    """
    console = Console()

    if not files_to_display:
        console.print(f"\n未发现超过指定大小的文件。")
        return

    console.print(f"\n发现超过指定大小的文件共 {total_found} 个。显示前 {len(files_to_display)} 个：\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=4)
    table.add_column("大小", justify="right", width=12)
    table.add_column("文件路径", justify="left")

    for i, (path, size) in enumerate(files_to_display, 1):
        formatted_size = format_size(size)
        table.add_row(str(i) + ".", formatted_size, path)

    console.print(table)
