"""Deduplication: checks generated puzzles against known NYT puzzles."""

import json
import logging
from pathlib import Path

from src.config import NYT_PUZZLES_PATH, DEDUP_WORD_OVERLAP_THRESHOLD

logger = logging.getLogger(__name__)


class Deduplicator:
    """Checks generated puzzles against the ground truth NYT dataset."""

    def __init__(self, nyt_path: str = None):
        self.nyt_path = nyt_path or NYT_PUZZLES_PATH
        self._nyt_puzzles = None

    @property
    def nyt_puzzles(self) -> list[dict]:
        if self._nyt_puzzles is None:
            self._nyt_puzzles = self._load_nyt_puzzles()
        return self._nyt_puzzles

    def _load_nyt_puzzles(self) -> list[dict]:
        path = Path(self.nyt_path)
        if not path.exists():
            logger.warning(f"NYT puzzles file not found at {self.nyt_path}; dedup disabled.")
            return []
        with open(path) as f:
            return json.load(f)

    def check(self, puzzle_words: list[str]) -> dict:
        """Check a puzzle's 16 words against all known NYT puzzles.

        Returns:
            {
                "is_duplicate": bool,
                "max_overlap": int,
                "overlapping_puzzle": str or None,
                "category_matches": list of matching category names
            }
        """
        words_upper = {w.upper() for w in puzzle_words}
        max_overlap = 0
        worst_match = None
        category_matches = []

        for nyt in self.nyt_puzzles:
            nyt_words = {w.upper() for w in nyt.get("words", [])}
            overlap = len(words_upper & nyt_words)
            if overlap > max_overlap:
                max_overlap = overlap
                worst_match = nyt.get("contest", nyt.get("date", "unknown"))

            # Check category name matches
            for answer in nyt.get("answers", []):
                cat = answer.get("answerDescription", "").upper()
                if cat:
                    category_matches.append(cat)

        is_dup = max_overlap > DEDUP_WORD_OVERLAP_THRESHOLD

        if is_dup:
            logger.warning(
                f"Duplicate detected: {max_overlap} words overlap with '{worst_match}'"
            )

        return {
            "is_duplicate": is_dup,
            "max_overlap": max_overlap,
            "overlapping_puzzle": worst_match if max_overlap > 0 else None,
            "category_matches": [],
        }
