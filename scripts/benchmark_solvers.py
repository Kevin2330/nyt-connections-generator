"""Benchmark embedding and clustering solvers on all 554 NYT puzzles.

Saves results to data/solver_benchmark.json and prints a summary.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import NYT_PUZZLES_PATH
from src.solvers.embedding_solver import EmbeddingSolver
from src.solvers.clustering_solver import ClusteringSolver
from src.solvers.roundtable import normalize_groups

COLORS = ["yellow", "green", "blue", "purple"]


def load_nyt():
    with open(NYT_PUZZLES_PATH) as f:
        return json.load(f)


def check_per_group(solver_groups, answer_groups):
    """Return a list of booleans — one per answer group (yellow, green, blue, purple)."""
    solver_sets = [frozenset(w.upper() for w in g["words"]) for g in solver_groups]
    results = []
    for ans in answer_groups:
        ans_set = frozenset(w.upper() for w in ans["words"])
        results.append(ans_set in solver_sets)
    return results


def run_benchmark():
    puzzles = load_nyt()
    n = len(puzzles)
    print(f"Loaded {n} NYT puzzles")

    # Load model once
    from sentence_transformers import SentenceTransformer
    print("Loading MPNET model...")
    model = SentenceTransformer("all-mpnet-base-v2")

    emb_solver = EmbeddingSolver(model=model)
    clust_solver = ClusteringSolver(model=model, beam_width=10)

    results = []

    # ── Embedding solver ────────────────────────────────────��───────────
    print(f"\n{'='*60}")
    print("Running EMBEDDING solver on {n} puzzles...".format(n=n))
    print(f"{'='*60}")
    emb_start = time.time()

    for i, puzzle in enumerate(puzzles):
        words = puzzle["words"]
        answers = puzzle["answers"]

        t0 = time.time()
        solution = emb_solver.solve(words)
        elapsed = time.time() - t0

        per_group = check_per_group(solution, answers)
        correct_count = sum(per_group)

        entry = {
            "puzzle_index": i,
            "date": puzzle.get("date", ""),
            "difficulty": puzzle.get("difficulty"),
            "embedding": {
                "groups_correct": correct_count,
                "fully_solved": correct_count == 4,
                "per_color": {COLORS[j]: per_group[j] for j in range(4)},
                "time_s": round(elapsed, 3),
            },
        }
        results.append(entry)

        if (i + 1) % 50 == 0 or i == 0:
            rate = (i + 1) / (time.time() - emb_start)
            eta = (n - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1:>3}/{n}] correct={correct_count}/4  "
                  f"({rate:.1f} puz/s, ETA {eta:.0f}s)")

    emb_elapsed = time.time() - emb_start
    print(f"Embedding solver done in {emb_elapsed:.1f}s")

    # ── Clustering solver ───────────────────────────────────��───────────
    print(f"\n{'='*60}")
    print("Running CLUSTERING solver on {n} puzzles...".format(n=n))
    print(f"{'='*60}")
    clust_start = time.time()

    for i, puzzle in enumerate(puzzles):
        words = puzzle["words"]
        answers = puzzle["answers"]

        t0 = time.time()
        solution = clust_solver.solve(words)
        elapsed = time.time() - t0

        per_group = check_per_group(solution, answers)
        correct_count = sum(per_group)

        results[i]["clustering"] = {
            "groups_correct": correct_count,
            "fully_solved": correct_count == 4,
            "per_color": {COLORS[j]: per_group[j] for j in range(4)},
            "time_s": round(elapsed, 3),
        }

        if (i + 1) % 50 == 0 or i == 0:
            rate = (i + 1) / (time.time() - clust_start)
            eta = (n - i - 1) / rate if rate > 0 else 0
            print(f"  [{i+1:>3}/{n}] correct={correct_count}/4  "
                  f"({rate:.1f} puz/s, ETA {eta:.0f}s)")

    clust_elapsed = time.time() - clust_start
    print(f"Clustering solver done in {clust_elapsed:.1f}s")

    # ── Compute aggregate stats ─────────────────────────────────────────
    summary = compute_summary(results, n)
    summary["timing"] = {
        "embedding_total_s": round(emb_elapsed, 1),
        "clustering_total_s": round(clust_elapsed, 1),
        "embedding_per_puzzle_s": round(emb_elapsed / n, 3),
        "clustering_per_puzzle_s": round(clust_elapsed / n, 3),
    }

    output = {"summary": summary, "per_puzzle": results}

    out_path = PROJECT_ROOT / "data" / "solver_benchmark.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {out_path}")

    print_summary(summary, n)
    return output


def compute_summary(results, n):
    summary = {}
    for solver in ["embedding", "clustering"]:
        fully_solved = sum(1 for r in results if r[solver]["fully_solved"])
        total_groups = sum(r[solver]["groups_correct"] for r in results)

        per_color_correct = {c: 0 for c in COLORS}
        per_color_total = {c: 0 for c in COLORS}
        for r in results:
            for c in COLORS:
                per_color_total[c] += 1
                if r[solver]["per_color"][c]:
                    per_color_correct[c] += 1

        per_color_acc = {
            c: round(per_color_correct[c] / per_color_total[c], 4) if per_color_total[c] else 0
            for c in COLORS
        }

        # Groups-correct distribution
        dist = [0, 0, 0, 0, 0]  # 0,1,2,3,4 correct
        for r in results:
            dist[r[solver]["groups_correct"]] += 1

        summary[solver] = {
            "full_puzzle_solve_rate": round(fully_solved / n, 4),
            "full_puzzle_solved": fully_solved,
            "avg_groups_correct": round(total_groups / n, 3),
            "total_groups_correct": total_groups,
            "per_color_accuracy": per_color_acc,
            "groups_correct_distribution": {str(k): dist[k] for k in range(5)},
        }

    # Agreement stats
    agree = sum(
        1 for r in results
        if set(tuple(sorted(r["embedding"]["per_color"][c] for c in COLORS)))
        == set(tuple(sorted(r["clustering"]["per_color"][c] for c in COLORS)))
        and r["embedding"]["fully_solved"] and r["clustering"]["fully_solved"]
    )
    both_solved = sum(
        1 for r in results
        if r["embedding"]["fully_solved"] and r["clustering"]["fully_solved"]
    )
    summary["agreement"] = {
        "both_fully_solved": both_solved,
        "both_fully_solved_rate": round(both_solved / n, 4),
    }

    return summary


def print_summary(summary, n):
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Puzzles: {n}")
    print()

    for solver in ["embedding", "clustering"]:
        s = summary[solver]
        print(f"  {solver.upper()} SOLVER:")
        print(f"    Full puzzle solve rate: {s['full_puzzle_solve_rate']:.1%}  ({s['full_puzzle_solved']}/{n})")
        print(f"    Avg groups correct:     {s['avg_groups_correct']:.2f} / 4")
        print(f"    Per-color accuracy:")
        for c in COLORS:
            acc = s["per_color_accuracy"][c]
            bar = "#" * int(acc * 30)
            print(f"      {c:>6}: {acc:>5.1%}  {bar}")
        print(f"    Groups-correct distribution:")
        for k in range(5):
            count = s["groups_correct_distribution"][str(k)]
            print(f"      {k}/4: {count:>3} puzzles ({count/n:.1%})")
        print()

    a = summary["agreement"]
    print(f"  SOLVER AGREEMENT:")
    print(f"    Both fully solved: {a['both_fully_solved']}/{n} ({a['both_fully_solved_rate']:.1%})")
    print(f"{'='*60}")


if __name__ == "__main__":
    run_benchmark()
