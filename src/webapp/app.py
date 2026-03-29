"""Flask backend for the Infinite Connections web app."""

import json
import os
import random
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, jsonify, request

from src.config import MOCK_PUZZLES_PATH, GENERATED_PUZZLES_PATH

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-fallback-key")

# Load puzzles at startup
_puzzles = []


def load_puzzles():
    """Load puzzles from generated or mock data."""
    global _puzzles

    # Try generated puzzles first
    gen_path = Path(GENERATED_PUZZLES_PATH)
    if gen_path.exists():
        for f in sorted(gen_path.glob("*.json")):
            with open(f) as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    _puzzles.extend(data)
                else:
                    _puzzles.append(data)

    # Fall back to mock puzzles
    if not _puzzles:
        mock_path = Path(MOCK_PUZZLES_PATH)
        if mock_path.exists():
            with open(mock_path) as f:
                _puzzles = json.load(f)

    print(f"Loaded {len(_puzzles)} puzzles")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/puzzle/random")
def random_puzzle():
    """Get a random puzzle."""
    if not _puzzles:
        return jsonify({"error": "No puzzles available"}), 404
    puzzle = random.choice(_puzzles)
    # Return only the shuffled words (not the answer)
    return jsonify({
        "id": puzzle["id"],
        "words": puzzle["words"],
        "num_groups": len(puzzle.get("groups", [])),
    })


@app.route("/api/puzzle/<puzzle_id>")
def get_puzzle(puzzle_id):
    """Get a specific puzzle by ID."""
    for p in _puzzles:
        if p["id"] == puzzle_id:
            return jsonify({
                "id": p["id"],
                "words": p["words"],
                "num_groups": len(p.get("groups", [])),
            })
    return jsonify({"error": "Puzzle not found"}), 404


@app.route("/api/puzzle/<puzzle_id>/check", methods=["POST"])
def check_guess(puzzle_id):
    """Check a guess of 4 words against a puzzle's groups."""
    data = request.get_json()
    guess = set(w.upper() for w in data.get("words", []))

    if len(guess) != 4:
        return jsonify({"error": "Must guess exactly 4 words"}), 400

    puzzle = None
    for p in _puzzles:
        if p["id"] == puzzle_id:
            puzzle = p
            break

    if not puzzle:
        return jsonify({"error": "Puzzle not found"}), 404

    # Check against each group
    for group in puzzle.get("groups", []):
        group_words = set(w.upper() for w in group["words"])
        if guess == group_words:
            return jsonify({
                "correct": True,
                "category": group["category"],
                "color": group.get("color", "yellow"),
                "words": group["words"],
            })

    # Check for "one away" (3 out of 4 match)
    best_overlap = 0
    for group in puzzle.get("groups", []):
        group_words = set(w.upper() for w in group["words"])
        overlap = len(guess & group_words)
        best_overlap = max(best_overlap, overlap)

    return jsonify({
        "correct": False,
        "one_away": best_overlap == 3,
    })


@app.route("/api/puzzle/<puzzle_id>/reveal")
def reveal_puzzle(puzzle_id):
    """Reveal the full solution for a puzzle."""
    for p in _puzzles:
        if p["id"] == puzzle_id:
            return jsonify({
                "id": p["id"],
                "groups": p.get("groups", []),
            })
    return jsonify({"error": "Puzzle not found"}), 404


@app.route("/api/puzzles")
def list_puzzles():
    """List all available puzzle IDs."""
    return jsonify({
        "puzzles": [
            {"id": p["id"], "method": p.get("metadata", {}).get("generation_method", "unknown")}
            for p in _puzzles
        ]
    })


if __name__ == "__main__":
    load_puzzles()
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Infinite Connections on http://localhost:{port}")
    app.run(debug=True, port=port)
