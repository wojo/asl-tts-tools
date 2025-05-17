"""Configuration handling for ASL TTS tools."""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Literal, Optional
import yaml

DEFAULT_CONFIG_PATH = "/etc/asl-tts-tools/config.yaml"


@dataclass
class Config:
    # Directory paths with defaults
    sounds_directory: Path = Path("/usr/share/asterisk/sounds/en")
    custom_sounds_directory: Path = Path("/usr/share/asterisk/sounds/custom/generated")
    cache_directory: Path = Path("/tmp/asl-tts-tools-cache")

    # Sound handling
    on_missing: Literal["error", "beep", "skip"] = "error"
    beep_sound: str = "beep"
    silence_sound: str = "silence/1"
    max_phrase_words_for_filenames: int = 5
    auto_phrase_matching: bool = True

    # TTS settings
    auto_generate_words: bool = True
    asl_tts_bin: str = "asl-tts"

    # Cache settings
    max_cache_files: int = 100  # -1 means no limit
    max_cache_age_days: int = -1  # -1 means no limit

    def __post_init__(self):
        """Validate and process config after initialization."""
        # Convert string paths to Path objects
        self.sounds_directory = Path(self.sounds_directory)
        self.custom_sounds_directory = Path(self.custom_sounds_directory)
        self.cache_directory = Path(self.cache_directory)

        # Validate settings
        if self.max_cache_files != -1 and self.max_cache_files < 0:
            raise ValueError("max_cache_files must be -1 or a positive number")

        if self.max_cache_age_days != -1 and self.max_cache_age_days < 0:
            raise ValueError("max_cache_age_days must be a positive number")

        if self.max_phrase_words_for_filenames < 1:
            raise ValueError("max_phrase_words_for_filenames must be a positive number")

        if not self.asl_tts_bin:
            raise ValueError("asl_tts_bin cannot be empty")

        if not self.beep_sound:
            raise ValueError("beep_sound cannot be empty")

        if not self.silence_sound:
            raise ValueError("silence_sound cannot be empty")

        # Create necessary directories
        self.custom_sounds_directory.mkdir(parents=True, exist_ok=True)
        self.cache_directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_file(cls, path: Optional[str] = None) -> "Config":
        """Create config from YAML file.

        Args:
            path: Path to YAML config file, or None for defaults

        Returns:
            Config object
        """
        if not path:
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)

    def to_dict(self):
        """Convert config to dictionary."""
        return {
            k: str(v) if isinstance(v, Path) else v for k, v in asdict(self).items()
        }
