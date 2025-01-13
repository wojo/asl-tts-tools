"""Asterisk integration utilities."""

from pathlib import Path
from .config import Config
from typing import Dict
import os
import sys

SUPPORTED_ASTERISK_SOUND_EXTENSIONS = [
    ".ul",
    ".ulaw",  # uLaw
    ".al",
    ".alaw",  # aLaw
    ".g711",  # G.711
    ".g723",  # G.723.1
    ".g726",  # G.726
    ".g729",  # G.729
    ".gsm",  # Raw GSM
    ".ilbc",  # iLBC codec
    ".pcm",  # Raw PCM
    ".sln",  # Signed Linear
    ".vox",  # Dialogic VOX
    ".wav",  # WAV format
    ".wav_gsm",  # WAV with GSM encoding
]

SKIP_PREFIXES = [".", "CREDITS", "LICENSE", "CHANGES", "README"]
SKIP_SUFFIXES = [".txt"]

NORMALIZATION_BLACKLIST = ["digits", "letters", "phonetic", "silence"]


def normalize_phrase(phrase: str) -> str:
    """Normalize a phrase by replacing underscores and hyphens with spaces, converting to lowercase, and remove any path that may exist.

    Does not normalize paths that start with:
        - digits/
        - letters/
        - phonetic/
        - silence/

    Args:
        phrase: The phrase to normalize

    Returns:
        The normalized phrase
    """
    path = Path(phrase)

    # Check if the path starts with any blacklisted prefixes
    if any(part in NORMALIZATION_BLACKLIST for part in path.parts):
        return str(path.with_suffix(""))

    # Get just the filename without extension or path
    phrase = path.stem

    # Convert to lowercase
    phrase = phrase.lower()

    # Replace underscores and hyphens with spaces
    phrase = phrase.replace("_", " ").replace("-", " ")

    # Remove any extra whitespace
    phrase = " ".join(phrase.split())

    return phrase


def _create_normalized_phrase_to_sound_file_mapping(
    base_files: Dict[str, str], custom_files: Dict[str, str], verbose: int = 0
) -> Dict[str, str]:
    """Create a mapping of normalized phrases to sound files.
    Custom files take priority over base files.

    Examples:
        "connected" -> "connected"
        "connected to" -> "connected to"
        "connected-to" -> "connected to"
        "connected_to" -> "connected to"
        "rpt/connected-to" -> "connected to"
        "connectedto" -> "connectedto"
        "rpt/connectedto" -> "connectedto"
    """
    normalized_phrases = {}

    # Process base files first
    for sound_file, sound_file_path in base_files.items():
        normalized_phrase = normalize_phrase(sound_file)
        if normalized_phrase in normalized_phrases:
            if verbose >= 1:
                print(
                    f"Warning: Normalized phrase '{normalized_phrase}' already exists in mapping at '{normalized_phrases[normalized_phrase]}', skipping '{sound_file_path}'"
                )
        else:
            normalized_phrases[normalized_phrase] = sound_file_path

    # Process custom files second (will override base files)
    for sound_file, sound_file_path in custom_files.items():
        normalized_phrase = normalize_phrase(sound_file)
        if normalized_phrase in normalized_phrases and verbose >= 1:
            print(
                f"Info: Custom file overriding base file for phrase '{normalized_phrase}': "
                f"{normalized_phrases[normalized_phrase]} -> {sound_file_path}"
            )
        normalized_phrases[normalized_phrase] = sound_file_path

    if verbose >= 2:
        print("Normalized phrase to sound file mapping:")
        for normalized_phrase, sound_file in normalized_phrases.items():
            print(f"  {normalized_phrase} -> {sound_file}")

    return normalized_phrases


def load_sound_files(config: Config, verbose: int = 0) -> Dict[str, str]:
    """Load available sound files from configured directories.

    Args:
        config: The configuration object
        verbose: The verbosity level

    Returns:
        A dictionary of available sound files, keyed by the normalized phrase and a value of the sound file path
    """
    base_sounds_directory_files = {}
    custom_sounds_directory_files = {}

    def load_from_directory(directory, files_dict):
        if verbose >= 1:
            print(f"Loading sounds from directory: {directory}")

        if not directory.exists():
            if verbose >= 1:
                print(f"Directory {directory} does not exist")
            return

        # Check if directory is readable
        if not os.access(directory, os.R_OK):
            raise PermissionError(f"Cannot read sounds directory: {directory}")

        for path in directory.rglob("*.*"):
            if any(path.name.startswith(prefix) for prefix in SKIP_PREFIXES) or any(
                path.name.endswith(suffix) for suffix in SKIP_SUFFIXES
            ):
                continue

            # Check if the file extension is supported by Asterisk
            if path.suffix.lower() in SUPPORTED_ASTERISK_SOUND_EXTENSIONS:
                # Check if file is readable
                if not os.access(path, os.R_OK):
                    print(f"Warning: Cannot read sound file: {path}", file=sys.stderr)
                    continue

                relative_path = str(path.relative_to(directory).with_suffix(""))
                files_dict[relative_path] = str(path)
            else:
                print(f"Skipping unsupported sound file: {path}")

            if verbose >= 3:
                print(f"  {relative_path} -> {path}")

        if verbose >= 1:
            print(f"Loaded {len(files_dict)} sound files from {directory}")

    # Load from base and custom sounds directories
    load_from_directory(config.sounds_directory, base_sounds_directory_files)
    load_from_directory(config.custom_sounds_directory, custom_sounds_directory_files)

    if len(base_sounds_directory_files) == 0:
        raise ValueError(
            f"No sound files found in base directory: {config.sounds_directory}"
        )

    if verbose >= 2:
        print(f"Available base sounds: {len(base_sounds_directory_files)}")
        if verbose >= 3:
            print("\nBase sounds:")
            for key in sorted(base_sounds_directory_files.keys()):
                print(f"  {key} -> {base_sounds_directory_files[key]}")
        print(f"Available custom sounds: {len(custom_sounds_directory_files)}")
        if verbose >= 3:
            print("\nCustom sounds:")
            for key in sorted(custom_sounds_directory_files.keys()):
                print(f"  {key} -> {custom_sounds_directory_files[key]}")

    normalized_phrase_to_sound_file_mapping = (
        _create_normalized_phrase_to_sound_file_mapping(
            base_sounds_directory_files, custom_sounds_directory_files, verbose
        )
    )

    return normalized_phrase_to_sound_file_mapping
