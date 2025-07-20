import os
import sys
from typing import Set, List

from path_handler import normalize_path


def get_user_exclusions(cli_exclusions: List[str], config_filename: str) -> Set[str]:
    """
    Loads exclusions from a config file and combines them with CLI arguments.
    Returns a set of raw user-provided paths.
    """
    config_exclusions = set()
    if os.path.isfile(config_filename):
        print(f"Found config file: '{config_filename}', loading exclusions...")
        with open(config_filename, 'r', encoding='utf-8') as f:
            for line in f:
                path = line.strip()
                if path and not path.startswith('#'):
                    config_exclusions.add(path)

    return set(cli_exclusions) | config_exclusions


def process_exclusions(
    base_exclusions: Set[str],
    user_exclusions: Set[str]
) -> tuple[Set[str], Set[str]]:
    """
    Normalizes and validates user-provided exclusion paths.

    Returns:
        A tuple containing:
        - The final, combined set of all lowercase, normalized exclusion paths.
        - A set of validated, absolute paths provided by the user for display.
    """
    validated_user_exclusions = set()
    final_exclusions = base_exclusions.copy()

    for user_path in user_exclusions:
        normalized_user_path = normalize_path(user_path)
        if os.path.isdir(normalized_user_path):
            final_exclusions.add(os.path.normpath(
                normalized_user_path).lower())
            validated_user_exclusions.add(normalized_user_path)
        else:
            print(
                f"Warning: Exclude path '{user_path}' from config or CLI is not a valid directory, ignoring.", file=sys.stderr)

    return final_exclusions, validated_user_exclusions
