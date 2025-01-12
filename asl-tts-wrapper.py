#!/usr/bin/env python3

import sys
import subprocess
import argparse
from pathlib import Path
import shutil

from asl_tts_lib.asl import play_via_asterisk
from asl_tts_lib.config import Config, DEFAULT_CONFIG_PATH
from asl_tts_lib.utils import cache_cleanup, sanitize_filename_with_hash


def main():
    parser = argparse.ArgumentParser(
        description="ASL TTS Wrapper with Asterisk Playback"
    )
    parser.add_argument("text", type=str, help="Text to convert to speech")
    parser.add_argument("-n", "--node", type=str, help="Node number")
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="Output file to save the combined audio, .ul extension will be added",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        default=DEFAULT_CONFIG_PATH,
        help="Path to config file",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (use -v or -vv)",
    )
    args = parser.parse_args()

    if not args.node and not args.file:
        parser.error("Either -n/--node or -f/--file (or both) must be specified")

    config = Config.from_file(args.config)
    verbose = args.verbose

    if verbose >= 1:
        print("Configuration Loaded:")
        for key, value in config.to_dict().items():
            print(f"  {key}: {value}")

    filename = sanitize_filename_with_hash(
        args.text, config.max_phrase_words_for_filenames
    )
    cache_file = config.cache_directory / f"{filename}.ul"

    if not cache_file.exists():
        cmd = [
            config.asl_tts_bin,
            "-n",
            args.node if args.node else "0",
            "-t",
            args.text,
            "-f",
            str(config.cache_directory / filename),
        ]
        if verbose >= 2:
            print(
                "Generating TTS file with command: "
                + " ".join([f'"{arg}"' if " " in arg else arg for arg in cmd])
            )
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error generating TTS: {e}", file=sys.stderr)
            if cache_file.exists():
                cache_file.unlink()
            sys.exit(2)
    else:
        if verbose >= 2:
            print(f"Using cached file: {cache_file}")

    if args.file:
        try:
            output_path = Path(args.file + ".ul")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cache_file, output_path)
            if verbose >= 2:
                print(f"Saved audio to: {output_path}")
        except Exception as e:
            print(f"Error saving output file: {e}", file=sys.stderr)
            sys.exit(2)

    if args.node:
        play_via_asterisk(cache_file, args.node, verbose)

        # Clean up old cache files
    if verbose >= 2:
        print("\nPerforming cache cleanup...")

    cache_cleanup(
        config.cache_directory,
        config.max_cache_age_days,
        config.max_cache_files,
        verbose,
    )


if __name__ == "__main__":
    main()
