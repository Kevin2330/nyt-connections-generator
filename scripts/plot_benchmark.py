"""Generate accuracy charts from solver benchmark results."""

import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

COLORS_ORDER = ["yellow", "green", "blue", "purple"]
COLOR_HEX = {"yellow": "#F9DF6D", "green": "#A0C35A", "blue": "#B0C4EF", "purple": "#BA81C5"}
SOLVER_COLORS = {"embedding": "#2176AE", "clustering": "#E84855"}

with open(PROJECT_ROOT / "data" / "solver_benchmark.json") as f:
    data = json.load(f)

summary = data["summary"]
per_puzzle = data["per_puzzle"]
n = len(per_puzzle)

out_dir = PROJECT_ROOT / "data"

# ── Figure 1: Per-Color Accuracy ────────────────────────────────────────

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(COLORS_ORDER))
width = 0.35

emb_acc = [summary["embedding"]["per_color_accuracy"][c] * 100 for c in COLORS_ORDER]
clust_acc = [summary["clustering"]["per_color_accuracy"][c] * 100 for c in COLORS_ORDER]

bars1 = ax.bar(x - width/2, emb_acc, width, label="Embedding Solver",
               color=SOLVER_COLORS["embedding"], alpha=0.85)
bars2 = ax.bar(x + width/2, clust_acc, width, label="Clustering Solver",
               color=SOLVER_COLORS["clustering"], alpha=0.85)

# Color the x-axis labels
ax.set_xticks(x)
labels = ax.set_xticklabels([c.capitalize() for c in COLORS_ORDER], fontsize=12, fontweight='bold')
for label, color in zip(labels, COLORS_ORDER):
    label.set_color({"yellow": "#B8960C", "green": "#5A7A1A",
                      "blue": "#4A6FA5", "purple": "#7A4988"}[color])

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.5, f"{h:.1f}%",
                ha='center', va='bottom', fontsize=10)

ax.set_ylabel("Accuracy (%)", fontsize=12)
ax.set_title("Per-Color Group Accuracy — Solver Benchmark on 554 NYT Puzzles", fontsize=14)
ax.legend(fontsize=11)
ax.set_ylim(0, 40)
ax.yaxis.set_major_formatter(mticker.PercentFormatter())
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.tight_layout()
fig.savefig(out_dir / "benchmark_per_color_accuracy.png", dpi=150, bbox_inches='tight')
print(f"Saved {out_dir / 'benchmark_per_color_accuracy.png'}")

# ── Figure 2: Groups-Correct Distribution ───────────────────────────────

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, solver, color in zip(axes, ["embedding", "clustering"],
                               [SOLVER_COLORS["embedding"], SOLVER_COLORS["clustering"]]):
    dist = summary[solver]["groups_correct_distribution"]
    counts = [dist[str(k)] for k in range(5)]
    pcts = [c / n * 100 for c in counts]

    bars = ax.bar(range(5), pcts, color=color, alpha=0.85, edgecolor="white", linewidth=1.5)
    for bar, pct, cnt in zip(bars, pcts, counts):
        if pct > 0:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                    f"{cnt}\n({pct:.1f}%)", ha='center', va='bottom', fontsize=9)

    ax.set_xticks(range(5))
    ax.set_xticklabels(["0/4", "1/4", "2/4", "3/4", "4/4"], fontsize=11)
    ax.set_xlabel("Groups Correct", fontsize=11)
    ax.set_ylabel("% of Puzzles", fontsize=11)
    solve_rate = summary[solver]["full_puzzle_solve_rate"] * 100
    avg_gc = summary[solver]["avg_groups_correct"]
    ax.set_title(f"{solver.capitalize()} Solver\n"
                 f"Solve rate: {solve_rate:.1f}% | Avg correct: {avg_gc:.2f}/4",
                 fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

plt.tight_layout()
fig.savefig(out_dir / "benchmark_groups_correct_dist.png", dpi=150, bbox_inches='tight')
print(f"Saved {out_dir / 'benchmark_groups_correct_dist.png'}")

# ── Figure 3: Head-to-Head Scatter ──────────────────────────────────────

fig, ax = plt.subplots(figsize=(7, 7))

emb_gc = [r["embedding"]["groups_correct"] for r in per_puzzle]
clust_gc = [r["clustering"]["groups_correct"] for r in per_puzzle]

# Jitter for overlapping points
jitter = 0.15
rng = np.random.default_rng(42)
emb_j = np.array(emb_gc) + rng.uniform(-jitter, jitter, n)
clust_j = np.array(clust_gc) + rng.uniform(-jitter, jitter, n)

ax.scatter(emb_j, clust_j, alpha=0.35, s=20, c="#333", edgecolors="none")
ax.plot([0, 4], [0, 4], "--", color="#ccc", linewidth=1, zorder=0)

ax.set_xlabel("Embedding Solver — Groups Correct", fontsize=12)
ax.set_ylabel("Clustering Solver — Groups Correct", fontsize=12)
ax.set_title("Head-to-Head: Embedding vs Clustering (554 puzzles)", fontsize=13)
ax.set_xticks(range(5))
ax.set_yticks(range(5))
ax.set_xlim(-0.5, 4.5)
ax.set_ylim(-0.5, 4.5)
ax.set_aspect("equal")
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Annotate quadrants
ax.text(3.5, 0.3, f"Emb only\n({sum(1 for e,c in zip(emb_gc,clust_gc) if e==4 and c<4)})",
        ha='center', fontsize=9, color='#666')
ax.text(0.3, 3.5, f"Clust only\n({sum(1 for e,c in zip(emb_gc,clust_gc) if c==4 and e<4)})",
        ha='center', fontsize=9, color='#666')
ax.text(3.5, 3.5, f"Both\n({sum(1 for e,c in zip(emb_gc,clust_gc) if e==4 and c==4)})",
        ha='center', fontsize=9, color='#666')

plt.tight_layout()
fig.savefig(out_dir / "benchmark_head_to_head.png", dpi=150, bbox_inches='tight')
print(f"Saved {out_dir / 'benchmark_head_to_head.png'}")

# ── Figure 4: Difficulty vs Accuracy ────────────────────────────────────

# Only for puzzles with a difficulty rating
rated = [(r["difficulty"], r["embedding"]["groups_correct"], r["clustering"]["groups_correct"])
         for r in per_puzzle if r["difficulty"] is not None]

if rated:
    fig, ax = plt.subplots(figsize=(10, 5))
    diffs, emb_g, clust_g = zip(*rated)

    # Bin by difficulty
    bins = np.arange(1.0, 5.5, 0.5)
    bin_labels = [f"{b:.1f}-{b+0.5:.1f}" for b in bins[:-1]]
    bin_idx = np.digitize(diffs, bins) - 1

    emb_means, clust_means = [], []
    for bi in range(len(bins) - 1):
        mask = [i for i, b in enumerate(bin_idx) if b == bi]
        if mask:
            emb_means.append(np.mean([emb_g[i] for i in mask]))
            clust_means.append(np.mean([clust_g[i] for i in mask]))
        else:
            emb_means.append(0)
            clust_means.append(0)

    x = np.arange(len(bin_labels))
    ax.bar(x - width/2, emb_means, width, label="Embedding",
           color=SOLVER_COLORS["embedding"], alpha=0.85)
    ax.bar(x + width/2, clust_means, width, label="Clustering",
           color=SOLVER_COLORS["clustering"], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(bin_labels, fontsize=10)
    ax.set_xlabel("Puzzle Difficulty Rating", fontsize=11)
    ax.set_ylabel("Avg Groups Correct", fontsize=11)
    ax.set_title("Solver Accuracy by Puzzle Difficulty (227 rated puzzles)", fontsize=13)
    ax.legend()
    ax.set_ylim(0, 4.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(out_dir / "benchmark_difficulty_vs_accuracy.png", dpi=150, bbox_inches='tight')
    print(f"Saved {out_dir / 'benchmark_difficulty_vs_accuracy.png'}")

print("\nAll charts generated.")
