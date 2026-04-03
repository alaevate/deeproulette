"""File-based training feed — reads roulette numbers from .txt files for batch training."""

import os
import re
import logging
from pathlib import Path

from config.settings import TRAINING_FILES_DIR


class FileFeed:
    """
    Scans TRAINING_FILES_DIR for .txt files, parses roulette numbers from each,
    and returns them as separate histories for per-file training & evaluation.

    Supported formats inside each .txt file:
      • One number per line:        17\\n5\\n0\\n32
      • Comma-separated on a line:  17, 5, 0, 32
      • Space-separated:            17 5 0 32
      • Mixed (any combination of the above)
      • Lines starting with # are ignored (comments)
    """

    def __init__(self, folder: str = None):
        self.folder = folder or TRAINING_FILES_DIR
        self._log = logging.getLogger("FileFeed")

    def discover_files(self) -> list[Path]:
        """Return sorted list of .txt files found in the training folder."""
        os.makedirs(self.folder, exist_ok=True)
        files = sorted(Path(self.folder).glob("*.txt"))
        self._log.info(f"Discovered {len(files)} training file(s) in {self.folder}")
        return files

    @staticmethod
    def parse_file(filepath: Path) -> list[int]:
        """
        Read a .txt file and extract all valid roulette numbers (0–36).

        Returns a list of ints in the order they appear.
        """
        numbers = []
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Extract all integers from the line
                tokens = re.findall(r"\d+", line)
                for tok in tokens:
                    n = int(tok)
                    if 0 <= n <= 36:
                        numbers.append(n)
        return numbers

    def load_all(self) -> list[dict]:
        """
        Discover + parse every file.

        Returns a list of dicts:
            [{"name": "casino_session_1.txt", "path": Path, "numbers": [17, 5, ...]}, ...]
        """
        results = []
        for fp in self.discover_files():
            nums = self.parse_file(fp)
            results.append({
                "name": fp.name,
                "path": fp,
                "numbers": nums,
            })
            self._log.info(f"  {fp.name}: {len(nums)} valid spins")
        return results
