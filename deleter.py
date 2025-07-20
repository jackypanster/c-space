import sys
import shutil
import logging
from pathlib import Path
from typing import List, Tuple

try:
    from send2trash import send2trash
except ImportError:
    print("错误: 未找到 'send2trash' 库。请运行 'pip install send2trash' 进行安装。", file=sys.stderr)
    sys.exit(1)

from utils import format_size

logger = logging.getLogger(__name__)


def interactive_delete(files_to_process: List[Tuple[str, int]]):
    """
    Starts an interactive loop to ask the user to delete files one by one.
    """
    if not files_to_process:
        return

    try:
        terminal_width = shutil.get_terminal_size().columns
    except OSError:
        terminal_width = 80

    logger.info("\n开始交互式删除...")
    logger.info("输入 'y' 删除, 'n' 或直接按 Enter 跳过, 'q' 退出。")

    for i, (path_str, size) in enumerate(files_to_process, 1):
        path = Path(path_str)
        if not path.exists():
            logger.warning(f"文件 '{path}' 已不存在，自动跳过。")
            continue

        formatted_size = format_size(size)

        prompt_prefix = f"[{i}] 删除 {formatted_size} 的文件 ''? (y/N/q): "
        available_width = terminal_width - len(prompt_prefix)
        display_path = str(path)
        if len(display_path) > available_width and available_width > 15:
            display_path = f"{display_path[:(available_width - 3)]}..."
        prompt = f"[{i}] 删除 {formatted_size} 的文件 '{display_path}'? (y/N/q): "

        try:
            answer = input(prompt).lower().strip()
        except (KeyboardInterrupt, EOFError):
            logger.info("\n操作已取消。")
            break

        if answer in ('y', 'yes'):
            try:
                send2trash(path)
                logger.info(f"> 成功将 '{path.name}' 移至回收站。")
            except Exception as e:
                logger.error(f"> 错误：删除 '{path.name}' 失败。原因: {e}")
        elif answer in ('q', 'quit'):
            logger.info("> 已退出删除流程。")
            break
        else:
            logger.info("> 已跳过。")

