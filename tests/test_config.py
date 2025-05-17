import unittest
import sys
from types import SimpleNamespace
sys.modules.setdefault('yaml', SimpleNamespace(safe_load=lambda f: {}))
from pathlib import Path
from asl_tts_lib.config import Config

class ConfigTests(unittest.TestCase):
    def test_default_init(self):
        cfg = Config()
        self.assertEqual(cfg.on_missing, "error")
        self.assertIsInstance(cfg.sounds_directory, Path)
        self.assertIsInstance(cfg.custom_sounds_directory, Path)
        self.assertIsInstance(cfg.cache_directory, Path)

if __name__ == "__main__":
    unittest.main()
