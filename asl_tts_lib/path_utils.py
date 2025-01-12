"""Path and filename normalization utilities."""

from pathlib import Path
from typing import Tuple


def normalize_sound_path(path: str) -> str:
    """Normalize a sound file path for consistent lookup.

    Args:
        path: Sound file path to normalize

    Returns:
        Normalized path suitable for lookup
    """
    path = path.lower()
    # TODO: What does this do?
    if any(c in path for c in ",."):
        return None
    return path


def get_normalized_keys(path: Path, relative_to: Path = None) -> Tuple[str, str]:
    """Get normalized keys for a sound file path.

    Args:
        path: Path to sound file
        relative_to: Optional base path to make path relative to

    Returns:
        Tuple of (relative path key, normalized phrase key)
    """
    # Get relative path without extension
    if relative_to:
        relative_path = str(path.relative_to(relative_to)).replace(path.suffix, "")
    else:
        relative_path = path.stem

    # Get normalized phrase version (for matching)
    if "/" in relative_path:
        normalized = relative_path.split("/")[-1].replace("-", " ")
    else:
        normalized = relative_path.replace("-", " ")

    return relative_path, normalized
