"""Audio file handling utilities."""

import subprocess
from pathlib import Path
from typing import List


def _get_format(file_path: str) -> str:
    """Get the format for a sound file based on extension.

    Args:
        file_path: Path to sound file

    Returns:
        Format string for sox
    """
    ext = Path(file_path).suffix.lower()
    format_map = {
        ".ul": "ul",
        ".ulaw": "ul",
        ".gsm": "gsm",
        ".wav": "wav",
        ".sln": "sln",
        ".g729": "g729",
    }
    return format_map.get(ext, "ul")  # Default to ul format


def concat_audio(files: List[str], output_path: str) -> None:
    """Concatenate audio files.

    Args:
        files: List of paths to audio files
        output_path: Path to write concatenated audio
    """
    if not files:
        return

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Build sox command with format for each file, silence warnings with -V0
    cmd = ["sox", "-V0"]
    for f in files:
        fmt = _get_format(f)
        cmd.extend(["-t", fmt, f])

    # Add output format
    out_fmt = _get_format(output_path)
    cmd.extend(["-t", out_fmt, output_path])

    subprocess.run(cmd, check=True)
