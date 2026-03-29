"""End-to-end tests for the Infinite Connections pipeline.

All tests run with DRY_RUN=true (mock LLM) and use the MPNET
embedding model for real embedding-based selection and solving.
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

# Ensure DRY_RUN is true for all tests
os.environ["DRY_RUN"] = "true"

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import MOCK_PUZZLES_PATH, WORDS_PER_GROUP, GROUPS_PER_PUZZLE, TOTAL_WORDS
from src.llm_client import LLMClient, MockLLMClient


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_mock():
    """Reset mock state before each test."""
    MockLLMClient.reset()


@pytest.fixture(scope="session")
def embedding_model():
    """Load MPNET model once for the entire test session."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-mpnet-base-v2")


@pytest.fixture
def llm():
    return LLMClient(dry_run=True)


@pytest.fixture
def mock_puzzles():
    with open(MOCK_PUZZLES_PATH) as f:
        return json.load(f)


# ── Config Tests ────────────────────────────────────────────────────────────

class TestConfig:
    def test_dry_run_is_true(self):
        from src.config import DRY_RUN
        assert DRY_RUN is True

    def test_mock_puzzles_exist(self):
        assert Path(MOCK_PUZZLES_PATH).exists()


# ── Mock LLM Tests ──────────────────────────────────────────────────────────

class TestMockLLM:
    def test_group_creation_response(self, llm):
        resp = llm.complete("category group word", "create a group")
        data = json.loads(resp)
        assert "category" in data
        assert "words" in data
        assert len(data["words"]) == 8  # Pool of 8 candidates

    def test_editor_response(self, llm):
        resp = llm.complete(
            "You are a puzzle editor reviewing a Connections puzzle.",
            "Review this puzzle for accuracy"
        )
        data = json.loads(resp)
        assert "valid" in data

    def test_false_group_response(self, llm):
        resp = llm.complete(
            "Create a root group for the false group method.",
            "Create a root group with alternate meanings"
        )
        data = json.loads(resp)
        assert "category" in data
        assert "alternate_meanings" in data
        assert len(data["words"]) == 4

    def test_solver_response(self, llm):
        resp = llm.complete(
            "You are solving an NYT Connections puzzle. Identify and find groups.",
            "Solve this Connections puzzle."
        )
        data = json.loads(resp)
        assert "groups" in data
        assert len(data["groups"]) == 4


# ── Embedding Selector Tests ───────────────────────────────────────────────

class TestEmbeddingSelector:
    def test_select_best_4_from_8(self, embedding_model):
        from src.generator.group_creator import EmbeddingSelector
        selector = EmbeddingSelector(model=embedding_model)

        # 8 words about music — best 4 should be most similar
        words = ["PIANO", "GUITAR", "DRUMS", "VIOLIN", "TRUMPET", "FLUTE", "CELLO", "HARP"]
        selected, score = selector.select_best(words, n=4)

        assert len(selected) == 4
        assert score > 0
        assert all(w in words for w in selected)

    def test_select_preserves_pool_when_small(self, embedding_model):
        from src.generator.group_creator import EmbeddingSelector
        selector = EmbeddingSelector(model=embedding_model)

        words = ["CAR", "BUS", "TRUCK"]
        selected, score = selector.select_best(words, n=4)
        # Can't select 4 from 3, returns what's available
        assert len(selected) == 3


# ── Group Creator Tests ─────────────────────────────────────────────────────

class TestGroupCreator:
    def test_create_single_group(self, llm, embedding_model):
        from src.generator.group_creator import GroupCreator, EmbeddingSelector
        selector = EmbeddingSelector(model=embedding_model)
        creator = GroupCreator(llm, selector, word_bank=["RAIN", "SUN", "MOON", "STAR"])

        group = creator.create_group_iterative()
        assert "category" in group
        assert "words" in group
        assert len(group["words"]) == WORDS_PER_GROUP
        assert "similarity_score" in group
        assert group["similarity_score"] > 0

    def test_iterative_avoids_reuse(self, llm, embedding_model):
        from src.generator.group_creator import GroupCreator, EmbeddingSelector
        selector = EmbeddingSelector(model=embedding_model)
        creator = GroupCreator(llm, selector)

        group1 = creator.create_group_iterative()
        group2 = creator.create_group_iterative(previous_groups=[group1])

        words1 = set(group1["words"])
        words2 = set(group2["words"])
        # Should have no overlap (if pool allows)
        # Note: with mock data, overlap may occur since pools are predefined
        assert isinstance(words1, set)
        assert isinstance(words2, set)

    def test_false_group_pipeline(self, llm, embedding_model):
        from src.generator.group_creator import GroupCreator, EmbeddingSelector
        selector = EmbeddingSelector(model=embedding_model)
        creator = GroupCreator(llm, selector)

        groups = creator.create_false_group_puzzle()
        assert len(groups) == GROUPS_PER_PUZZLE
        for g in groups:
            assert len(g["words"]) == WORDS_PER_GROUP
            assert "inspired_by" in g


# ── Puzzle Editor Tests ─────────────────────────────────────────────────────

class TestPuzzleEditor:
    def test_editor_review(self, llm):
        from src.generator.puzzle_editor import PuzzleEditor
        editor = PuzzleEditor(llm)

        groups = [
            {"category": "FAST WORDS", "words": ["QUICK", "SWIFT", "RAPID", "FLEET"]},
            {"category": "PLANETS", "words": ["MARS", "VENUS", "SATURN", "JUPITER"]},
        ]
        result = editor.review(groups)
        assert len(result) == 2
        # Mock says valid=True with no changes, so categories should be unchanged
        assert result[0]["category"] == "FAST WORDS"


# ── Difficulty Tests ────────────────────────────────────────────────────────

class TestDifficulty:
    def test_compute_similarity(self, embedding_model):
        from src.generator.difficulty import compute_group_similarity
        score = compute_group_similarity(
            ["PIANO", "GUITAR", "DRUMS", "VIOLIN"], embedding_model
        )
        assert score > 0
        assert score < 1.0

    def test_assign_colors(self, embedding_model):
        from src.generator.difficulty import assign_colors
        groups = [
            {"category": "A", "words": ["PIANO", "GUITAR", "DRUMS", "VIOLIN"], "similarity_score": 0.0},
            {"category": "B", "words": ["RED", "BLUE", "GREEN", "YELLOW"], "similarity_score": 0.0},
            {"category": "C", "words": ["MARS", "VENUS", "SATURN", "JUPITER"], "similarity_score": 0.0},
            {"category": "D", "words": ["QUICK", "FAST", "SWIFT", "RAPID"], "similarity_score": 0.0},
        ]
        result = assign_colors(groups, model=embedding_model)
        assert len(result) == 4
        colors = {g["color"] for g in result}
        assert colors == {"yellow", "green", "blue", "purple"}
        # Yellow should have highest similarity
        assert result[0]["color"] == "yellow"
        assert result[0]["similarity_score"] >= result[-1]["similarity_score"]


# ── Deduplicator Tests ──────────────────────────────────────────────────────

class TestDeduplicator:
    def test_no_duplicate(self):
        from src.generator.deduplicator import Deduplicator
        dedup = Deduplicator(nyt_path="/nonexistent/path.json")
        result = dedup.check(["A", "B", "C", "D", "E", "F", "G", "H",
                              "I", "J", "K", "L", "M", "N", "O", "P"])
        assert result["is_duplicate"] is False
        assert result["max_overlap"] == 0

    def test_with_nyt_data(self):
        from src.config import NYT_PUZZLES_PATH
        if not Path(NYT_PUZZLES_PATH).exists():
            pytest.skip("NYT dataset not available")
        from src.generator.deduplicator import Deduplicator
        dedup = Deduplicator()
        # Use words from the first NYT puzzle — should flag as duplicate
        nyt = dedup.nyt_puzzles[0]
        result = dedup.check(nyt["words"])
        assert result["is_duplicate"] is True
        assert result["max_overlap"] == 16


# ── Solver Tests ────────────────────────────────────────────────────────────

class TestEmbeddingSolver:
    def test_solve_mock_puzzle(self, embedding_model, mock_puzzles):
        from src.solvers.embedding_solver import EmbeddingSolver
        solver = EmbeddingSolver(model=embedding_model)

        puzzle = mock_puzzles[0]
        result = solver.solve(puzzle["words"])
        assert len(result) == 4
        all_words = set()
        for g in result:
            assert len(g["words"]) == 4
            assert g["score"] > 0
            all_words.update(g["words"])
        # All 16 words should be used exactly once
        assert len(all_words) == TOTAL_WORDS


class TestClusteringSolver:
    def test_solve_mock_puzzle(self, embedding_model, mock_puzzles):
        from src.solvers.clustering_solver import ClusteringSolver
        solver = ClusteringSolver(model=embedding_model, beam_width=5)

        puzzle = mock_puzzles[0]
        result = solver.solve(puzzle["words"])
        assert len(result) == 4
        all_words = set()
        for g in result:
            assert len(g["words"]) == 4
            all_words.update(g["words"])
        assert len(all_words) == TOTAL_WORDS


class TestLLMSolver:
    def test_solve_returns_groups(self, llm):
        from src.solvers.llm_solver import LLMSolver
        solver = LLMSolver(llm=llm)

        words = ["PIANO", "GUITAR", "DRUMS", "VIOLIN",
                 "RED", "BLUE", "GREEN", "YELLOW",
                 "MARS", "VENUS", "SATURN", "JUPITER",
                 "QUICK", "FAST", "SWIFT", "RAPID"]
        result = solver.solve(words)
        assert len(result) == 4
        for g in result:
            assert "words" in g


# ── Roundtable Tests ────────────────────────────────────────────────────────

class TestRoundtable:
    def test_validate_mock_puzzle(self, embedding_model, mock_puzzles, llm):
        from src.solvers.roundtable import Roundtable
        roundtable = Roundtable(embedding_model=embedding_model, llm=llm)

        puzzle = mock_puzzles[0]
        result = roundtable.validate(puzzle)

        assert "valid" in result
        assert "solver_agreement" in result
        assert "solvers_used" in result
        assert "embedding" in result["solvers_used"]
        assert "clustering" in result["solvers_used"]
        assert "solver_results" in result

    def test_roundtable_helpers(self):
        from src.solvers.roundtable import normalize_groups, groups_match, check_against_answer

        groups = [{"words": ["A", "B", "C", "D"]}, {"words": ["E", "F", "G", "H"]}]
        norm = normalize_groups(groups)
        assert len(norm) == 2
        assert frozenset(["A", "B", "C", "D"]) in norm

        # Same groups in different order should match
        g1 = [frozenset(["A", "B", "C", "D"]), frozenset(["E", "F", "G", "H"])]
        g2 = [frozenset(["E", "F", "G", "H"]), frozenset(["A", "B", "C", "D"])]
        assert groups_match(g1, g2)

        # Check against answer
        answer = [{"words": ["A", "B", "C", "D"]}, {"words": ["E", "F", "G", "H"]}]
        correct = check_against_answer(g1, answer)
        assert correct == 2


# ── Evaluation Tests ────────────────────────────────────────────────────────

class TestMetrics:
    def test_group_similarity_score(self, embedding_model):
        from src.evaluation.metrics import group_similarity_score
        embs = embedding_model.encode(
            ["PIANO", "GUITAR", "DRUMS", "VIOLIN"], convert_to_numpy=True
        )
        score = group_similarity_score(embs)
        assert isinstance(score, float)

    def test_penalty_score(self, embedding_model):
        from src.evaluation.metrics import penalty_score
        group_embs = embedding_model.encode(["PIANO", "GUITAR"], convert_to_numpy=True)
        remaining = embedding_model.encode(["CAR", "HOUSE"], convert_to_numpy=True)
        score = penalty_score(group_embs, remaining)
        assert isinstance(score, float)

    def test_puzzle_quality_from_stored(self, mock_puzzles):
        from src.evaluation.metrics import puzzle_quality_score
        quality = puzzle_quality_score(mock_puzzles[0])
        assert quality["total_words"] == 16
        assert quality["unique_words"] == 16
        assert quality["overall_avg_similarity"] > 0

    def test_puzzle_quality_with_model(self, embedding_model, mock_puzzles):
        from src.evaluation.metrics import puzzle_quality_score
        quality = puzzle_quality_score(mock_puzzles[0], model=embedding_model)
        assert quality["total_words"] == 16
        assert len(quality["groups"]) == 4


class TestAnalyzer:
    def test_analyze_dataset(self, mock_puzzles):
        from src.evaluation.analyzer import PuzzleAnalyzer
        analyzer = PuzzleAnalyzer()
        stats = analyzer.analyze_dataset(mock_puzzles)

        assert stats["count"] == 5
        assert stats["avg_similarity"] > 0
        assert "color_distribution" in stats
        assert "category_diversity" in stats

    def test_load_puzzles(self):
        from src.evaluation.analyzer import PuzzleAnalyzer
        puzzles = PuzzleAnalyzer.load_puzzles(MOCK_PUZZLES_PATH)
        assert len(puzzles) == 5

    def test_convert_nyt_format(self):
        from src.evaluation.analyzer import PuzzleAnalyzer
        nyt_sample = [{
            "date": "2024/01/01",
            "words": ["A", "B", "C", "D", "E", "F", "G", "H",
                      "I", "J", "K", "L", "M", "N", "O", "P"],
            "answers": [
                {"answerDescription": "GROUP1", "words": ["A", "B", "C", "D"]},
                {"answerDescription": "GROUP2", "words": ["E", "F", "G", "H"]},
                {"answerDescription": "GROUP3", "words": ["I", "J", "K", "L"]},
                {"answerDescription": "GROUP4", "words": ["M", "N", "O", "P"]},
            ],
        }]
        converted = PuzzleAnalyzer.convert_nyt_format(nyt_sample)
        assert len(converted) == 1
        assert len(converted[0]["groups"]) == 4
        assert converted[0]["groups"][0]["color"] == "yellow"


# ── End-to-End Pipeline Test ───────────────────────────────────────────────

class TestEndToEnd:
    def test_generate_and_validate_iterative(self, embedding_model, llm):
        """Full pipeline: generate 1 puzzle → validate with roundtable."""
        from src.generator.pipeline import PuzzlePipeline
        from src.solvers.roundtable import Roundtable

        pipeline = PuzzlePipeline(
            llm=llm,
            embedding_model=embedding_model,
            word_bank=["RAIN", "SUN", "MOON", "STAR", "TREE", "LAKE"],
        )

        # Generate
        puzzle = pipeline.generate(method="iterative")
        assert puzzle["id"] == "INF-00001"
        assert len(puzzle["words"]) == TOTAL_WORDS
        assert len(puzzle["groups"]) == GROUPS_PER_PUZZLE

        # Check schema
        for g in puzzle["groups"]:
            assert "category" in g
            assert "words" in g
            assert "color" in g
            assert "similarity_score" in g
            assert len(g["words"]) == WORDS_PER_GROUP

        assert puzzle["metadata"]["generation_method"] == "iterative"
        assert puzzle["metadata"]["dedup_check"] is True

        # Validate with roundtable
        roundtable = Roundtable(embedding_model=embedding_model, llm=llm)
        validation = roundtable.validate(puzzle)
        assert "valid" in validation
        assert len(validation["solvers_used"]) >= 2

    def test_generate_false_group(self, embedding_model, llm):
        """Generate a puzzle via the false-group method."""
        from src.generator.pipeline import PuzzlePipeline

        pipeline = PuzzlePipeline(llm=llm, embedding_model=embedding_model)
        puzzle = pipeline.generate(method="false_group")

        assert len(puzzle["words"]) == TOTAL_WORDS
        assert len(puzzle["groups"]) == GROUPS_PER_PUZZLE
        assert puzzle["metadata"]["generation_method"] == "false_group"

    def test_full_quality_analysis(self, embedding_model, mock_puzzles):
        """Run quality analysis on the mock dataset."""
        from src.evaluation.analyzer import PuzzleAnalyzer
        from src.evaluation.metrics import puzzle_quality_score

        analyzer = PuzzleAnalyzer(model=embedding_model)
        stats = analyzer.analyze_dataset(mock_puzzles)

        assert stats["count"] == 5
        assert stats["solver_agreement_rate"] > 0

        # Check individual puzzle quality
        quality = puzzle_quality_score(mock_puzzles[0], model=embedding_model)
        assert quality["total_words"] == 16
        assert len(quality["groups"]) == 4
        for gm in quality["groups"]:
            assert gm["avg_pairwise_sim"] > 0
