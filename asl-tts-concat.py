#!/usr/bin/env python3
import argparse
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List

from asl_tts_lib.config import Config, DEFAULT_CONFIG_PATH
from asl_tts_lib.tokenizer import tokenize_text
from asl_tts_lib.matcher import find_sound_matches
from asl_tts_lib.audio import concat_audio
from asl_tts_lib.sounds import load_sound_files
from asl_tts_lib.asl import play_via_asterisk
from asl_tts_lib.utils import cache_cleanup, sanitize_filename_with_hash


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c", "--config", help="Path to config file", default=DEFAULT_CONFIG_PATH
    )
    parser.add_argument("-f", "--file", help="Output file path")
    parser.add_argument("-n", "--node", help="Asterisk node number for playback")
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for verbose, -vv for very verbose)",
    )
    parser.add_argument(
        "-g",
        "--generate-tts",
        action="store_true",
        help="Auto-generate TTS for missing words",
    )
    parser.add_argument("text", nargs="?", help="Text to speak")
    args = parser.parse_args()

    if not args.node and not args.file:
        parser.error("Either -n/--node or -f/--file (or both) must be specified")

    # Load config
    config = Config.from_file(args.config)
    config_dict = config.to_dict()

    if args.verbose >= 1:
        print("Configuration:")
        for key, value in config_dict.items():
            print(f"  {key}: {value}")

    # Override auto-generate setting if specified
    if args.generate_tts:
        config_dict["auto_generate_words"] = True

    # Load available sound files
    sounds = load_sound_files(config, args.verbose)

    # Get text from stdin if not provided as argument
    text = args.text
    if not text:
        text = sys.stdin.read().strip()

    if not text:
        parser.error("No text provided")

    if args.verbose >= 1:
        print(f"Text: {text}")

    # Tokenize text
    tokens = tokenize_text(text)
    if args.verbose >= 1:
        print(f"Initial tokens: {tokens}")

    # Find matching sound files
    matches = find_sound_matches(tokens, sounds, config_dict, args.verbose)

    # Create cache file for concatenated audio
    filename = sanitize_filename_with_hash(
        text, config_dict["max_phrase_words_for_filenames"]
    )
    cache_file = Path(config_dict["cache_directory"]) / f"{filename}.ul"

    # Concatenate audio files
    concat_audio(matches, str(cache_file))

    # Save output file if requested
    if args.file:
        shutil.copy2(cache_file, args.file)
        if args.verbose >= 1:
            print(f"Wrote output to {args.file}")

    # Play via Asterisk if node specified
    if args.node:
        play_via_asterisk(str(cache_file), args.node, args.verbose)

    # Clean up old cache files
    if args.verbose >= 2:
        print("\nPerforming cache cleanup...")
    cache_cleanup(
        config_dict["cache_directory"],
        config_dict["max_cache_age_days"],
        config_dict["max_cache_files"],
        args.verbose,
    )


if __name__ == "__main__":
    main()
