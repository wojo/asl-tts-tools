"""Text tokenization utilities for ASL TTS."""

from typing import List
from .constants import PAUSE_CHARS


def _is_word_token(token: str) -> bool:
    """Check if a token is a word (contains letters/numbers and optionally hyphens)."""
    if not token:
        return False

    return all(c.isalnum() or c == "-" for c in token) and any(
        c.isalnum() for c in token
    )


def _normalize_braced_content(text: str, brace_type: str) -> str:
    """Normalize content inside braces by trimming whitespace and collapsing spaces.

    Args:
        text: Text inside braces to normalize
        brace_type: Type of brace ('[', '{', or '(')

    Returns:
        Normalized text with consistent whitespace
    """
    # Strip outer braces
    inner = text[1:-1]

    # Normalize whitespace - collapse multiple spaces and trim
    normalized = " ".join(inner.split())

    # Add braces back
    if brace_type == "[":
        return f"[{normalized}]"
    elif brace_type == "{":
        return f"{{{normalized}}}"
    else:  # '('
        return f"({normalized})"


def tokenize_text(text: str, verbose: int = 0) -> List[str]:
    """Split text into tokens for sound matching.

    Args:
        text: Text to split into tokens
        verbose: Verbosity level (0=none, 1=basic, 2=detailed)

    Returns:
        List of tokens

    Rules:
        - Preserves [ABC] syntax for phonetic synthesis
        - Preserves {word} syntax for exact file matching
        - Preserves (phrase here) syntax for phrase grouping
        - Splits on spaces
        - Preserves hyphenated words (e.g. connected-to, D-Star)
        - Splits special characters into individual tokens
        - Preserves all pause characters for later matching
        - Normalizes whitespace inside braces/parentheses
    """
    if verbose >= 2:
        print(f"Tokenizing text: {text}")

    tokens = []
    current_token = ""
    inside_braces = False
    brace_type = None  # Track which type of brace we're inside

    # First pass: split on spaces and handle braced content
    for char in text:
        if inside_braces:
            current_token += char
            # Check for matching closing brace
            if (
                (char == "]" and brace_type == "[")
                or (char == "}" and brace_type == "{")
                or (char == ")" and brace_type == "(")
            ):
                # Normalize the braced content before adding
                normalized = _normalize_braced_content(current_token, brace_type)
                tokens.append(normalized)
                if verbose >= 2:
                    print(f"Found braced content: {normalized}")
                current_token = ""
                inside_braces = False
                brace_type = None
            continue

        if char in "[{(":
            if current_token:
                tokens.append(current_token)
                if verbose >= 2:
                    print(f"Adding token before brace: {current_token}")
            current_token = char
            inside_braces = True
            brace_type = char
            continue

        if char.isspace():
            if current_token:
                tokens.append(current_token)
                if verbose >= 2:
                    print(f"Adding token before space: {current_token}")
                current_token = ""
            continue

        current_token += char

    if current_token:
        tokens.append(current_token)
        if verbose >= 2:
            print(f"Adding final token: {current_token}")

    # Second pass: handle special characters in non-word tokens
    final_tokens = []
    for token in tokens:
        if token.startswith("[") or token.startswith("{") or token.startswith("("):
            final_tokens.append(token)
            if verbose >= 2:
                print(f"Keeping braced token: {token}")
            continue

        if _is_word_token(token):
            final_tokens.append(token)
            if verbose >= 2:
                print(f"Keeping word token: {token}")
            continue

        # Split special characters
        current = ""
        for char in token:
            if char.isalnum() or char == "-":
                # If we see a hyphen that's not part of a word, treat it as a pause char
                if char == "-" and (
                    not current or not any(c.isalnum() for c in current)
                ):
                    if current:
                        final_tokens.append(current)
                        if verbose >= 2:
                            print(f"Adding current before hyphen: {current}")
                        current = ""
                    # Only add the hyphen if it's not already the last token
                    if not final_tokens or final_tokens[-1] != "-":
                        final_tokens.append("-")
                        if verbose >= 2:
                            print("Adding hyphen token")
                else:
                    current += char
            else:
                if current:
                    final_tokens.append(current)
                    if verbose >= 2:
                        print(f"Adding current before special: {current}")
                    current = ""
                if char in PAUSE_CHARS:
                    # Only add pause char if it's not already the last token
                    if not final_tokens or final_tokens[-1] != char:
                        final_tokens.append(char)
                        if verbose >= 2:
                            print(f"Adding pause char: {char}")
                else:
                    final_tokens.append(char)
                    if verbose >= 2:
                        print(f"Adding special char: {char}")

        if current:
            final_tokens.append(current)
            if verbose >= 2:
                print(f"Adding final current: {current}")

    result = [t for t in final_tokens if t]
    if verbose >= 1:
        print(f"Final tokens: {result}")
    return result
