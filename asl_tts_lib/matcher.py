"""Sound file matching utilities."""

from typing import Dict, List, Optional, Tuple, Any
import sys
from asl_tts_lib.config import Config
from asl_tts_lib.sounds import normalize_phrase
from asl_tts_lib.tokenizer import _is_word_token
from asl_tts_lib.tts import should_generate_phrase, generate_missing_phrase
from asl_tts_lib.utils import sanitize_filename_with_hash
from .constants import CHAR_TO_DIGIT_MAP, CHAR_TO_LETTER_MAP, PAUSE_CHARS
import os


def find_sound_matches(
    tokens: List[str], sounds: Dict[str, str], config: Config, verbose: int = 0
) -> List[str]:
    """Find matching sound files for tokens.

    Args:
        tokens: List of tokens to match
        sounds: Dictionary mapping normalized phrases to full file paths
        config: Configuration object
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        List of paths to matching sound files
    """
    matches = []
    i = 0

    while i < len(tokens):
        if verbose >= 2:
            print(f"\nTrying to match token: {tokens[i]}")

        # Try parenthesized phrase - strongest match
        if tokens[i].startswith("(") and tokens[i].endswith(")"):
            phrase = tokens[i][1:-1]  # Remove parentheses
            normalized_phrase = sanitize_filename_with_hash(
                phrase, config.max_phrase_words_for_filenames
            )
            if normalized_phrase in sounds:
                path = sounds[normalized_phrase]
                if verbose >= 1:
                    print(f"Found exact match for '{tokens[i]}' -> {normalized_phrase}")
                matches.append(path)
                i += 1
                continue
            elif should_generate_phrase(phrase, verbose):
                tts_match = generate_missing_phrase(
                    phrase, normalized_phrase, config, verbose
                )
                if tts_match:
                    matches.append(tts_match)
                    i += 1
                    continue

        # Try exact match (e.g. {rpt/connected-to})
        elif tokens[i].startswith("{") and tokens[i].endswith("}"):
            path = normalize_phrase(tokens[i][1:-1])
            if path in sounds:
                if verbose >= 1:
                    print(f"Found exact match for '{tokens[i]}' -> {path}")
                matches.append(sounds[path])
                i += 1
                continue

        # Try uppercase word as individual letters first
        if tokens[i].isupper() and tokens[i].isalpha():
            letter_matches = _try_letter_match(tokens[i], sounds, verbose)
            if letter_matches:
                matches.extend(letter_matches)
                i += 1
                continue

        # Try phonetic match (e.g. [ABC])
        elif tokens[i].startswith("[") and tokens[i].endswith("]"):
            phonetic_matches = _try_phonetic_match(tokens[i], sounds, verbose)
            if phonetic_matches:
                matches.extend(phonetic_matches)
                i += 1
                continue

        # Try digit sequence
        elif tokens[i].isdigit():
            digit_matches = _try_digit_match(tokens[i], sounds, verbose)
            if digit_matches:
                matches.extend(digit_matches)
                i += 1
                continue

        # Try punctuation/special characters
        elif len(tokens[i]) == 1 and not tokens[i].isalnum():
            if tokens[i] in PAUSE_CHARS:
                if config.silence_sound in sounds:
                    if verbose >= 1:
                        print(
                            f"Using silence sound for '{tokens[i]}' -> {config.silence_sound}"
                        )
                    matches.append(sounds[config.silence_sound])
                    i += 1
                    continue
            else:
                if tokens[i] in CHAR_TO_DIGIT_MAP:
                    key = f"digits/{CHAR_TO_DIGIT_MAP[tokens[i]]}"
                    if key in sounds:
                        if verbose >= 1:
                            print(f"Found digit sound match for '{tokens[i]}' -> {key}")
                        matches.append(sounds[key])
                        i += 1
                        continue
                elif tokens[i] in CHAR_TO_LETTER_MAP:
                    key = f"letters/{CHAR_TO_LETTER_MAP[tokens[i]]}"
                    if key in sounds:
                        if verbose >= 1:
                            print(
                                f"Found letter sound match for '{tokens[i]}' -> {key}"
                            )
                        matches.append(sounds[key])
                        i += 1
                        continue

        # Try mixed alphanumeric as individual chars (e.g. A1, 1B)
        elif any(c.isalnum() for c in tokens[i]) and not any(
            c.islower() for c in tokens[i]
        ):
            mixed_matches = _try_mixed_match(tokens[i], sounds, verbose)
            if mixed_matches:
                matches.extend(mixed_matches)
                i += 1
                continue

        # Try phrase match - but don't skip other token matches
        phrase_match, consumed = _try_phrase_match(tokens[i:], sounds, verbose)
        if phrase_match:
            matches.append(phrase_match)
            i += consumed
            continue

        # Try TTS generation for words with lowercase letters
        if any(c.islower() for c in tokens[i]):
            if should_generate_phrase(tokens[i], verbose):
                normalized_phrase = sanitize_filename_with_hash(
                    tokens[i], config.max_phrase_words_for_filenames
                )
                tts_match = generate_missing_phrase(
                    tokens[i], normalized_phrase, config, verbose
                )
                if tts_match:
                    matches.append(tts_match)
                    i += 1
                    continue

        # If no match found, handle based on config
        if verbose >= 1:
            print(f"No match found for token: {tokens[i]}")

        if config.on_missing == "error":
            raise ValueError(f"No match found for token: {tokens[i]}")
        elif config.on_missing == "beep":
            if config.beep_sound in sounds:
                if verbose >= 1:
                    print(f"Using beep sound for '{tokens[i]}' -> {config.beep_sound}")
                matches.append(sounds[config.beep_sound])
            else:
                print(
                    f"Warning: Beep sound not found: {config.beep_sound}",
                    file=sys.stderr,
                )
        elif config.on_missing == "skip":
            i += 1
            continue
        else:
            raise ValueError(f"Invalid on_missing value: {config.on_missing}")

    return matches


def _try_phonetic_match(
    token: str, sounds: Dict[str, str], verbose: int = 0
) -> Optional[List[str]]:
    """Try to find phonetic matches for a token.

    Args:
        token: Token to match (e.g. [ABC])
        sounds: Dictionary of available sound files
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        List of paths to matching sound files if found, None otherwise
    """
    if not (token.startswith("[") and token.endswith("]")):
        return None

    chars = token[1:-1]  # Remove brackets
    matches = []

    for char in chars:
        # Skip spaces in phonetic sequences
        if not char.isalnum():
            continue

        if char.isdigit():
            key = f"digits/{char}"
        else:
            key = f"phonetic/{char.lower()}_p"

        if key in sounds:
            if verbose >= 1:
                print(f"Found phonetic match: {char} -> {key}")
            matches.append(sounds[key])
        else:
            if verbose >= 1:
                print(f"No phonetic match found for: {char}")
            return None

    return matches if matches else None


def _try_digit_match(
    token: str, sounds: Dict[str, str], verbose: int = 0
) -> Optional[List[str]]:
    """Try to find digit matches for a token.

    Args:
        token: Token to match (e.g. "123")
        sounds: Dictionary of available sound files
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        List of paths to matching sound files if found, None otherwise
    """
    if not token.isdigit():
        return None

    matches = []
    for digit in token:
        key = f"digits/{digit}"
        if key in sounds:
            if verbose >= 1:
                print(f"Found digit match: {digit} -> {key}")
            matches.append(sounds[key])
        else:
            return None

    return matches if matches else None


def _get_letter_key(char: str, sounds: Dict[str, str]) -> Optional[str]:
    """Get the key for a letter sound.

    Args:
        char: Character to look up
        sounds: Dictionary of available sound files

    Returns:
        Key if found, None otherwise
    """
    # Try all possible paths for the letter
    possible_keys = [
        f"letters/{char.lower()}",  # Try letters/ prefix first
        char.lower(),  # Try just the letter
        f"alpha/{char.lower()}",  # Try alpha/ prefix
        f"phonetic/{char.lower()}_p",  # Try phonetic as last resort
    ]

    for key in possible_keys:
        if key in sounds:
            return key

    return None


def _get_digit_key(char: str) -> str:
    """Get the key for a digit sound.

    Args:
        char: Digit character

    Returns:
        Key for digit sound
    """
    return f"digits/{char}"


def _try_mixed_match(
    token: str, sounds: Dict[str, str], verbose: int = 0
) -> Optional[List[str]]:
    """Try to match mixed alphanumeric token.

    Args:
        token: Token to match (e.g. "A1B2")
        sounds: Dictionary of available sound files
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        List of paths to matching sound files if found, None otherwise
    """
    matches = []
    for char in token:
        if char.isdigit():
            key = _get_digit_key(char)
        elif char.isalpha():
            key = _get_letter_key(char, sounds)
            if key is None:
                if verbose >= 1:
                    print(f"No match found for char: {char}")
                return None
        else:
            # Skip non-alphanumeric
            continue

        if key in sounds:
            if verbose >= 1:
                print(f"Found char match: {char} -> {key}")
            matches.append(sounds[key])
        else:
            if verbose >= 1:
                print(f"No match found for char: {char}")
            return None

    return matches if matches else None


def _try_letter_match(
    token: str, sounds: Dict[str, str], verbose: int = 0
) -> Optional[List[str]]:
    """Try to match individual letters in a token.

    Args:
        token: Token to match (e.g. "ABC")
        sounds: Dictionary of available sound files
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        List of paths to matching sound files if found, None otherwise
    """
    if not token.isalpha():  # Allow both upper and lowercase
        return None

    matches = []

    for letter in token:
        key = _get_letter_key(letter, sounds)
        if key is None:
            if verbose >= 1:
                print(f"No letter match found for: {letter}")
            # Don't break - keep trying other letters
            continue

        if key in sounds:
            if verbose >= 1:
                print(f"Found letter match: {letter} -> {key}")
            matches.append(sounds[key])

    # Return whatever matches we found, even if not all letters matched
    return matches if matches else None


def _try_phrase_match(
    tokens: List[str], sounds: Dict[str, str], verbose: int = 0
) -> Tuple[Optional[str], int]:
    """Try to find a phrase match starting at the first token and working backwards to find the longest possible match.

    Args:
        tokens: List of tokens to try matching
        sounds: Dictionary of available sound files
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        Tuple of (matching file path or None, number of tokens consumed)
    """
    if not tokens:
        return None, 0

    if verbose >= 2:
        print(f"Trying phrase match for tokens: {tokens}")

    max_length = len(tokens)

    # Find the first non-word token, if any
    for i, token in enumerate(tokens):
        if not _is_word_token(token):
            max_length = i
            break

    if verbose >= 2 and max_length < len(tokens):
        print(
            f"Limited tokens due to non-word token, remaining tokens: {tokens[:max_length]}"
        )

    for length in range(max_length, 0, -1):
        phrase = normalize_phrase(" ".join(tokens[:length]).lower())
        if verbose >= 2:
            print(f"Trying phrase: {phrase}")
        if phrase in sounds:
            if verbose >= 1:
                print(f"Found phrase match: {' '.join(tokens[:length])} -> {phrase}")
            return sounds[phrase], length

    if verbose >= 2:
        print("No phrase match found")
    return None, 0


def _generate_tts(phrase: str, tts_path: str, tts_engine: Any, verbose: int = 0) -> str:
    """Generate TTS for a phrase if it doesn't exist."""
    if verbose >= 1:
        print(f"Generating TTS for phrase: {phrase}")

    # Just generate the TTS - no need to check permissions multiple times
    os.makedirs(os.path.dirname(tts_path), exist_ok=True)
    tts_engine.save_to_file(phrase, tts_path)
    tts_engine.runAndWait()
    return tts_path
