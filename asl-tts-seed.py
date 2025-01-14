#!/usr/bin/env python3
"""Generate common sound chunks for ASL TTS tools."""

import argparse
import string
import sys
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import subprocess
from typing import Iterator, List, Tuple, Dict
from asl_tts_lib.config import Config, DEFAULT_CONFIG_PATH
from asl_tts_lib.utils import sanitize_filename_with_hash


# Type for text-to-filename mappings
TextMapping = Tuple[str, str]  # (filename, text)


# Sound chunk generators
def generate_letters() -> Iterator[TextMapping]:
    """Generate individual letter sounds A-Z."""
    mappings = {
        "a": "alpha",
        "b": "bravo",
        "c": "charlie",
        "d": "delta",
        "e": "echo",
        "f": "foxtrot",
        "g": "golf",
        "h": "hotel",
        "i": "india",
        "j": "juliet",
        "k": "kilo",
        "l": "lima",
        "m": "mike",
        "n": "november",
        "o": "oscar",
        "p": "papa",
        "q": "quebec",
        "r": "romeo",
        "s": "sierra",
        "t": "tango",
        "u": "uniform",
        "v": "victor",
        "w": "whiskey",
        "x": "x-ray",
        "y": "yankee",
        "z": "zulu",
    }
    for letter, text in mappings.items():
        yield letter, text


def generate_digits() -> Iterator[TextMapping]:
    """Generate individual digits and common numbers."""
    for num in range(1, 100):
        yield str(num), str(num)


def generate_phonetic() -> Iterator[TextMapping]:
    """Generate NATO phonetic alphabet."""
    phonetic = [
        "alpha",
        "bravo",
        "charlie",
        "delta",
        "echo",
        "foxtrot",
        "golf",
        "hotel",
        "india",
        "juliet",
        "kilo",
        "lima",
        "mike",
        "november",
        "oscar",
        "papa",
        "quebec",
        "romeo",
        "sierra",
        "tango",
        "uniform",
        "victor",
        "whiskey",
        "x-ray",
        "yankee",
        "zulu",
    ]
    for word in phonetic:
        yield word, word


def generate_time() -> Iterator[TextMapping]:
    """Generate time-related phrases."""
    mappings = {
        "oclock": "o'clock",
        "morning": "morning",
        "afternoon": "afternoon",
        "evening": "evening",
        "night": "night",
        "day": "day",
    }
    yield from mappings.items()


def generate_calendar() -> Iterator[TextMapping]:
    """Generate calendar-related words."""
    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    weekdays = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for word in months + weekdays:
        yield word, word


def generate_symbols() -> Iterator[TextMapping]:
    """Generate common symbols and punctuation."""
    mappings = {
        "exclamation": "exclamation",
        "question": "question",
        "asterisk": "asterisk",
        "at": "at",
        "ampersand": "and",
        "percent": "percent",
        "dollar": "dollar",
        "pound": "pound",
        "plus": "plus",
        "minus": "minus",
        "equals": "equals",
        "slash": "slash",
    }
    yield from mappings.items()


def generate_common_phrases() -> Iterator[TextMapping]:
    """Generate common ASL-related phrases."""
    mappings = {
        # Connection status
        "connected-to": "connected to",
        "disconnected-from": "disconnected from",
        "connecting": "connecting",
        "disconnecting": "disconnecting",
        # Node related
        "node": "node",
        "nodes": "nodes",
        "repeater": "repeater",
        "link": "link",
        # Status messages
        "online": "online",
        "offline": "offline",
        "enabled": "enabled",
        "disabled": "disabled",
        "activated": "activated",
        "deactivated": "deactivated",
        # Common responses
        "affirmative": "affirmative",
        "negative": "negative",
        "confirmed": "confirmed",
        "invalid": "invalid",
        "error": "error",
        "warning": "warning",
        # Courtesy phrases
        "please-wait": "please wait",
        "thank-you": "thank you",
        "goodbye": "goodbye",
        "hello": "hello",
        "welcome": "welcome",
        "please-try-again": "please try again",
    }
    yield from mappings.items()


def generate_rpt_phrases() -> Iterator[TextMapping]:
    """Generate AllStarLink rpt-specific phrases."""
    mappings = {
        # Timing and warnings
        "act-timeout-warning": "activity timeout warning",
        "timeout-warning": "timeout warning",
        "timeout": "timeout",
        "unkeyedfor": "unkeyed for",
        "keyedfor": "keyed for",
        # Connection status
        "alllinksdisconnected": "all links disconnected",
        "alllinksrestored": "all links restored",
        "connection_failed": "connection failed",
        "connected": "connected",
        "connected-to": "connected to",
        # Node status
        "node_enabled": "node enabled",
        "node": "node",
        "up": "up",
        "down": "down",
        # Power levels
        "hipwr": "high power",
        "medpwr": "medium power",
        "lopwr": "low power",
        # Remote operations
        "remote_already": "remote already",
        "remote_busy": "remote busy",
        "remote_cmd": "remote command",
        "remote_disc": "remote disconnect",
        "remote_go": "remote go",
        "remote_monitor": "remote monitor",
        "remote_notfound": "remote not found",
        "remote_tx": "remote transmit",
        # Time of day
        "goodmorning": "good morning",
        "goodafternoon": "good afternoon",
        "goodevening": "good evening",
        # Measurements
        "frequency": "frequency",
        "latitude": "latitude",
        "longitude": "longitude",
        "thetemperatureis": "the temperature is",
        "thetimeis": "the time is",
        "thevoltageis": "the voltage is",
        "thewindis": "the wind is",
        # Patch operations
        "autopatch_on": "autopatch on",
        "revpatch-intro": "reverse patch introduction",
        "revpatch-noanswer": "reverse patch no answer",
        # Misc status
        "functioncomplete": "function complete",
        "invalid-freq": "invalid frequency",
        "localmonitor": "local monitor",
        "memory_notfound": "memory not found",
        "repeat_only": "repeat only",
        "rxpl": "receive PL",
        "txpl": "transmit PL",
        "seconds": "seconds",
        "simplex": "simplex",
        "sitenorm": "site normal",
        "stop": "stop",
        "tranceive": "transceive",
        "version": "version",
    }
    yield from mappings.items()


def generate_custom_phrases(phrases_file: Path) -> Iterator[TextMapping]:
    """Generate phrases from a custom file.

    Args:
        phrases_file: Path to file containing phrases, one per line
        Format: filename->text or just text (in which case filename=text)
    """
    if not phrases_file.exists():
        print(f"Error: Phrases file not found: {phrases_file}", file=sys.stderr)
        return

    with open(phrases_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line:
                    filename, text = line.split("->", 1)
                    yield filename.strip(), text.strip()
                else:
                    yield line, line


def generate_tts(
    filename: str,
    text: str,
    output_file: Path,
    config: Config,
    verbose: int = 0,
    force: bool = False,
) -> Tuple[str, float, bool]:
    """Generate TTS for a single phrase.

    Args:
        filename: Filename to use (without extension)
        text: Text to generate
        output_file: Output file path
        config: Configuration object
        verbose: Verbosity level
        force: Whether to force regeneration

    Returns:
        Tuple of (text, time taken, success)
    """
    start_time = time.time()

    # Skip if file exists and not forcing
    if output_file.exists() and not force:
        return text, 0.0, False

    try:
        cmd = [
            config.asl_tts_bin,
            "-n",
            "1",
            "-t",
            text,
            "-f",
            str(output_file.with_suffix("")),
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return text, time.time() - start_time, True
    except subprocess.CalledProcessError as e:
        print(f"Error generating TTS for {text}: {e}", file=sys.stderr)
        if e.stderr:
            print(f"stderr: {e.stderr.decode()}", file=sys.stderr)
        return text, time.time() - start_time, False


def generate_chunks(
    config: Config,
    verbose: int = 0,
    force: bool = False,
    threads: int = None,
    phrases_file: Path = None,
):
    """Generate all sound chunks.

    Args:
        config: Configuration object
        verbose: Verbosity level
        force: Whether to force regeneration
        threads: Number of threads to use
        phrases_file: Optional path to file with custom phrases
    """
    # Map of category to generator function
    generators = [
        ("letters", generate_letters()),
        ("numbers", generate_digits()),
        ("phonetic", generate_phonetic()),
        ("time", generate_time()),
        ("calendar", generate_calendar()),
        ("symbols", generate_symbols()),
        ("phrases", generate_common_phrases()),
        ("rpt", generate_rpt_phrases()),
    ]

    # Add custom phrases if specified
    if phrases_file:
        generators.append(("custom", generate_custom_phrases(phrases_file)))

    # Create work items
    work_items = []
    for category, generator in generators:
        # Create category directory
        category_dir = config.custom_sounds_directory / category
        category_dir.mkdir(parents=True, exist_ok=True)

        for filename, text in generator:
            # Create safe filename if not in rpt category
            if category != "rpt":
                filename = sanitize_filename_with_hash(
                    filename, config.max_phrase_words_for_filenames
                )
            output_file = category_dir / f"{filename}.ul"
            work_items.append((filename, text, output_file))

    # Process work items
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(
                generate_tts, filename, text, output_file, config, verbose, force
            )
            for filename, text, output_file in work_items
        ]

        for future, (filename, text, _) in zip(as_completed(futures), work_items):
            text, duration, generated = future.result()
            if generated:
                print(f"Generating '{text}' -> '{filename}': Done ({duration:.1f}s)")
            else:
                print(
                    f"Generating '{text}' -> '{filename}': Skipping, file already exists"
                )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-c", "--config", help="Path to config file", default=DEFAULT_CONFIG_PATH
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (-v for verbose, -vv for very verbose)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force regeneration of existing files",
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=os.cpu_count(),
        help="Number of threads to use (default: number of CPUs, 1 to disable threading)",
    )
    parser.add_argument(
        "-p",
        "--phrases",
        type=Path,
        help="Path to file containing additional phrases (one per line, optionally filename->text)",
    )
    args = parser.parse_args()

    # Check config file exists
    if not Path(args.config).exists():
        sys.exit(f"Error: Config file not found: {args.config}")

    # Load config
    config = Config.from_file(args.config)

    # Check TTS binary exists and is executable
    tts_bin = Path(config.asl_tts_bin)
    if not tts_bin.is_absolute():
        tts_path = subprocess.which(config.asl_tts_bin)
        if not tts_path:
            sys.exit(f"Error: TTS binary not found in PATH: {config.asl_tts_bin}")
    elif not tts_bin.exists():
        sys.exit(f"Error: TTS binary not found: {config.asl_tts_bin}")

    # Generate chunks
    generate_chunks(
        config,
        verbose=args.verbose,
        force=args.force,
        threads=args.threads,
        phrases_file=args.phrases,
    )


if __name__ == "__main__":
    main()
