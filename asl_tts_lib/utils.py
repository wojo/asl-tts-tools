import re
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timedelta


def normalize_key(key: str) -> str:
    """Normalize a key by converting to lowercase and handling special cases.

    Args:
        key: The string key to normalize

    Returns:
        A normalized version of the key with special characters handled
        and consistent casing
    """
    key = key.lower()
    if any(c in key for c in ",."):
        return key

    parts = key.replace("-", " ").replace("_", " ").split()
    return " ".join(
        (
            part
            if part.isdigit()
            else "".join(c for c in part if c.isalnum() or c.isspace())
        )
        for part in parts
    ).strip()


def sanitize_filename_with_hash(text: str, max_words: int) -> str:
    """Create a safe filename from text with hash.

    Args:
        text: The text to convert into a safe filename
        max_words: Maximum number of words to include in filename

    Returns:
        A sanitized filename with an MD5 hash appended only if text exceeds max_words
    """
    words = text.split()
    needs_hash = len(words) > max_words

    # Take first max_words if needed
    if needs_hash:
        shortened_text = " ".join(words[:max_words])
    else:
        shortened_text = " ".join(words)

    # Sanitize by removing all non-alphanumeric chars except hyphens
    sanitized = re.sub(
        r"[^a-z0-9\-]", "", re.sub(r"[ _]+", "-", shortened_text.lower())
    )

    # Remove any trailing hyphen
    sanitized = sanitized.rstrip("-")

    # Ensure we have some content
    if not sanitized:
        sanitized = "text"

    # Only add hash if we truncated the text
    if needs_hash:
        hash_digest = hashlib.md5(text.encode("utf-8")).hexdigest()[:8]
        return f"{sanitized}-{hash_digest}"
    else:
        return sanitized


def cache_cleanup(
    cache_dir: str, max_age_days: int, max_files: int, verbose: int = 0
) -> None:
    """Clean up cache files based on age and count.

    Args:
        cache_dir: Directory containing cached files
        max_age_days: Maximum age in days before files are deleted (-1 for unlimited)
        max_files: Maximum number of files to keep in cache (-1 for unlimited)
        verbose: If True, print detailed information about cleanup

    Note:
        First removes files older than max_age_days, then removes oldest files
        if count exceeds max_files. Only processes files with .ul extension.
        Setting either max_age_days or max_files to -1 disables that limit.
    """
    # If both limits are disabled, nothing to do
    if max_age_days == -1 and max_files == -1:
        if verbose >= 2:
            print("Cache cleanup skipped - no limits set")
        return

    cache_path = Path(cache_dir)

    try:
        # Delete old files first if age limit is enabled
        if max_age_days != -1:
            now = datetime.now()
            cutoff_date = now - timedelta(days=max_age_days)
            files = sorted(
                [(f, f.stat().st_mtime) for f in cache_path.glob("*")],
                key=lambda x: x[1],
            )
            for file_path, mtime in files:
                if datetime.fromtimestamp(mtime) < cutoff_date:
                    if verbose:
                        print(f"Deleting (age): {file_path}")
                    file_path.unlink(missing_ok=True)

        # Then check if we need to delete any files based on count if count limit is enabled
        if max_files != -1:
            remaining_files = sorted(
                [(f, f.stat().st_mtime) for f in cache_path.glob("*")],
                key=lambda x: x[1],
            )
            if len(remaining_files) > max_files:
                files_to_delete = remaining_files[: (len(remaining_files) - max_files)]
                for file_path, _ in files_to_delete:
                    if verbose:
                        print(f"Deleting (count): {file_path}")
                    file_path.unlink(missing_ok=True)

    except Exception as e:
        if verbose:
            print(f"Warning: Cache cleanup error: {e}", file=sys.stderr)
        else:
            print(f"Error during cache cleanup: {e}", file=sys.stderr)
