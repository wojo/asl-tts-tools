"""Text-to-speech generation utilities."""

import os
import subprocess
from pathlib import Path
from typing import Optional
from .utils import sanitize_filename_with_hash, normalize_key


def should_generate_phrase(phrase: str, verbose: int = 0) -> bool:
    """Determine if a phrase should be generated via TTS.

    Args:
        phrase: Phrase to check
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        True if word should be generated via TTS

    Rules:
        - Skip pure numbers
        - Skip all uppercase words
        - Skip single characters
        - Allow words with any lowercase letters
        - Allow normal words and hyphenated words
        - Allow phrases in parentheses
    """
    # Always allow phrases in parentheses
    if phrase.startswith("(") and phrase.endswith(")"):
        if verbose >= 2:
            print(f"Allowing TTS for parenthesized phrase: {phrase}")
        return True

    # Skip pure numbers
    if phrase.replace("-", "").isdigit():
        if verbose >= 2:
            print(f"Skipping TTS for pure number: {phrase}")
        return False

    # Skip all uppercase phrases
    if phrase.isupper():
        if verbose >= 2:
            print(f"Skipping TTS for uppercase phrase: {phrase}")
        return False

    # Skip single characters
    if len(phrase) == 1:
        if verbose >= 2:
            print(f"Skipping TTS for single character: {phrase}")
        return False

    # Allow if contains any lowercase
    if any(c.islower() for c in phrase):
        if verbose >= 2:
            print(f"Allowing TTS for phrase with lowercase: {phrase}")
        return True

    if verbose >= 2:
        print(f"Skipping TTS for phrase: {phrase}")
    return False


def generate_missing_phrase(
    phrase: str, normalized_phrase: str, config: dict, verbose: int = 0
) -> Optional[str]:
    """Generate TTS for a missing phrase.

    Args:
        phrase: Original phrase to generate TTS for
        normalized_phrase: Normalized phrase to use for TTS
        config: Configuration dictionary
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        Path to generated sound file if successful, None otherwise
    """

    custom_dir = Path(config["custom_sounds_directory"])

    # For phrases in parentheses, strip them and use normalized version
    if phrase.startswith("(") and phrase.endswith(")"):
        # Strip parentheses and normalize
        inner_phrase = phrase[1:-1]
        normalized = normalize_key(inner_phrase)
    else:
        # For regular phrases, use the phrase directly but normalized
        normalized = normalize_key(phrase)

    # Create sanitized filename
    base_filename = sanitize_filename_with_hash(
        normalized, config["max_phrase_words_for_filenames"]
    )
    base_path = custom_dir / base_filename

    # Check if file already exists
    if base_path.with_suffix(".ul").exists():
        if verbose >= 1:
            print(f"Found existing TTS file for phrase: {phrase}")
        return str(base_path.with_suffix(".ul"))

    # Generate TTS using configured command
    try:
        tts_bin = config.get("asl_tts_bin", "asl-tts")

        # For phrases, use the inner content without parentheses
        tts_text = inner_phrase if phrase.startswith("(") else phrase

        cmd = [tts_bin, "-n", "1", "-t", tts_text, "-f", str(base_path)]
        if verbose >= 2:
            print(f"Running TTS command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        if verbose >= 1:
            print(f"Generated TTS file for phrase: {phrase}")
        # Return path with .ul since we know asl-tts adds it
        return str(base_path.with_suffix(".ul"))
    except subprocess.CalledProcessError as e:
        if verbose >= 1:
            print(f"Failed to generate TTS for phrase: {phrase}")
            print(f"Error: {e}")
        return None
