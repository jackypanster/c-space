import sys
from pathlib import Path
from typing import Set, List

from path_handler import normalize_path


def get_user_exclusions(cli_exclusions: List[str], config_filename: str) -> Set[str]:
    """
    Loads exclusions from a config file and combines them with CLI arguments.
    Returns a set of raw user-provided paths.
    """
    config_exclusions = set()
    config_file = Path(config_filename)
    if config_file.is_file():
        print(f"Found config file: '{config_filename}', loading exclusions...")
        with config_file.open('r', encoding='utf-8') as f:
            for line in f:
                path = line.strip()
                if path and not path.startswith('#'):
                    config_exclusions.add(path)

    return set(cli_exclusions) | config_exclusions


def process_exclusions(
    base_exclusions: Set[str],
    user_exclusions: Set[str]
) -> tuple[Set[str], Set[Path]]:
    """
    Normalizes and validates user-provided exclusion paths.

    Returns:
        A tuple containing:
        - The final, combined set of all lowercase, normalized exclusion paths (as strings).
        - A set of validated, absolute Path objects provided by the user for display.
    """
    validated_user_paths = set()
    final_exclusions_str = {p.lower() for p in base_exclusions}

    for user_path_str in user_exclusions:
        normalized_path = normalize_path(user_path_str)
        if normalized_path.is_dir():
            final_exclusions_str.add(str(normalized_path).lower())
            validated_user_paths.add(normalized_path)
        else:
            print(
                f"Warning: Exclude path '{user_path_str}' from config or CLI is not a valid directory, ignoring.", file=sys.stderr)

    return final_exclusions_str, validated_user_paths
