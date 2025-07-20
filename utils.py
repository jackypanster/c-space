import re

# Windows-specific file attribute constants, used by the scanner
FILE_ATTRIBUTE_HIDDEN = 0x02
FILE_ATTRIBUTE_SYSTEM = 0x04


def parse_size(size_str: str) -> int:
    """
    Parses a human-readable size string (e.g., '100MB', '2GB') into bytes.
    """
    size_str = size_str.strip().upper()
    match = re.match(r'^(\d+(\.\d+)?)\s*(B|KB|MB|GB|TB)$', size_str)
    if not match:
        raise ValueError(
            f"Invalid size format: '{size_str}'. Use B, KB, MB, GB, TB.")

    value = float(match.group(1))
    unit = match.group(3)

    units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    return int(value * units[unit])


def format_size(size_bytes: int) -> str:
    """
    Formats a size in bytes into a human-readable string (e.g., '1.23 GB').
    """
    if size_bytes is None or size_bytes < 0:
        return "N/A"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    for unit in ['KB', 'MB', 'GB', 'TB']:
        size_bytes /= 1024.0
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
    return f"{size_bytes:.2f} PB"  # For extremely large files
