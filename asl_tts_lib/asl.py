"""Asterisk integration utilities."""

import sys
import subprocess
from pathlib import Path
from .constants import EXIT_CODES
from typing import Dict


def play_via_asterisk(file_path: str, node_number: str, verbose: int = 0) -> None:
    """Play audio through Asterisk.

    Args:
        file_path: Path to audio file to play
        node_number: The Asterisk node number to play on
        verbose: The verbosity level
    """
    if not file_path:
        return

    try:
        bare_sound_path = str(Path(file_path).with_suffix("").resolve())
        command = f'asterisk -rx "rpt localplay {node_number} {bare_sound_path}"'
        if verbose:
            print(f"Executing: {command}")
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error playing audio via Asterisk: {e}", file=sys.stderr)
        sys.exit(EXIT_CODES["PLAYBACK_ERROR"])
