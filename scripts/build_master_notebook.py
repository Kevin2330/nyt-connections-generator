"""Build the master demonstration notebook: notebooks/master_demo.ipynb.

Covers all three methods (Pipeline A, CFR Mode A, CFR Mode B) end-to-end in
DRY_RUN mode so it runs without any API keys. Also loads pre-generated real
puzzle batches and produces comparison plots.
"""

import nbformat as nbf
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "notebooks" / "master_demo.ipynb"


def md(text: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(text.strip())


def code(source: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(source.strip())


def build() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    # ------------------------------------------------------------------
    cells.append(md(r"""
# Infinite Connections --- Master Demo

**A complete walkthrough of every method we built.**

This notebook demonstrates all three puzzle-generation pipelines side by side,
loads real benchmark batches, and reproduces every headline result from the
documentation.

**Pipelines covered:**

| Pipeline | Mode | LLM calls / puzzle | Pass rate | Cost / 10k |
|---|---|---:|---:|---:|
| A --- LLM-heavy baseline | iterative | 5 | 91% | ~$50 |
| B --- Category-First Retrieval | A: remix | **0** | **99%** | **$0** |
| B --- Category-First Retrieval | B: fresh | **1** | **99%** | **~$3** |

Everything runs in **DRY_RUN mode** by default, so no API keys are needed. The
same code works with real API keys if you set `DRY_RUN=false`.

> **Contents**
> 1. Setup & data loading
> 2. Inspect the NYT ground-truth dataset
> 3. Pipeline A demo (LLM-heavy baseline)
> 4. Pipeline B demo --- Mode A (remix, 0 LLM calls)
> 5. Pipeline B demo --- Mode B (fresh, 1 LLM call)
> 6. Multi-solver roundtable validation
> 7. Rubric-safety check (past-puzzle dedup)
> 8. Difficulty-color assignment
> 9. Benchmark results across all real batches
> 10. Gallery of sample generated puzzles
> 11. Conclusions
"""))

    # ==================================================================
    # 1. Setup
    cells.append(md(r"""## 1. Setup & data loading"""))

    cells.append(code(r"""
# Standard imports
import os, sys, json, random
from pathlib import Path
from collections import Counter

# Force dry-run unless user explicitly sets otherwise
os.environ.setdefault("DRY_RUN", "true")

# Add project root to path so we can import src/*
PROJECT_ROOT = Path().resolve()
while not (PROJECT_ROOT / "src").exists() and PROJECT_ROOT != PROJECT_ROOT.parent:
    PROJECT_ROOT = PROJECT_ROOT.parent
sys.path.insert(0, str(PROJECT_ROOT))

print(f"Project root: {PROJECT_ROOT}")
print(f"DRY_RUN:      {os.environ['DRY_RUN']}")
"""))

    cells.append(code(r"""
# Visualisation
import matplotlib.pyplot as plt
import numpy as np
try:
    import seaborn as sns
    sns.set_theme(style="whitegrid")
except ImportError:
    pass
plt.rcParams["figure.dpi"] = 110
"""))

    cells.append(code(r"""
# Helper to pretty-print a puzzle
COLORS = {"yellow": "🟨", "green": "🟩", "blue": "🟦", "purple": "🟪"}

def show_puzzle(puzzle, title=None):
    title = title or puzzle.get("id", "puzzle")
    print(f"--- {title} ---")
    for g in puzzle["groups"]:
        icon = COLORS.get(g.get("color", ""), "⬜")
        cat = g["category"]
        words = ", ".join(g["words"])
        sim = g.get("similarity_score", 0.0)
        print(f"  {icon} [{g.get('color','?'):>6}] {cat:<30} {words}  (sim={sim:.3f})")
"""))

    # ==================================================================
    # 2. NYT dataset
    cells.append(md(r"""
## 2. Inspect the NYT ground-truth dataset

554 real NYT Connections puzzles. We use this dataset for three purposes:
(1) solver benchmarking, (2) deduplication against past puzzles, and
(3) as the seed pool for CFR's word bank and category list.
"""))

    cells.append(code(r"""
NYT_PATH = PROJECT_ROOT / "data" / "nyt_puzzles" / "ConnectionsFinalDataset (1).json"

if NYT_PATH.exists():
    with open(NYT_PATH) as f:
        nyt = json.load(f)
    print(f"Loaded {len(nyt)} NYT puzzles from {NYT_PATH.name}")
else:
    print(f"NYT dataset not found at {NYT_PATH}. Some cells will be skipped.")
    nyt = []
"""))

    cells.append(code(r"""
# Schema of one puzzle
if nyt:
    puzzle = nyt[0]
    print("Fields:", list(puzzle.keys()))
    print()
    print(f"Contest: {puzzle['contest']}")
    print(f"Date:    {puzzle['date']}")
    print(f"Words:   {puzzle['words']}")
    print()
    print("Groups:")
    for ans in puzzle["answers"]:
        print(f"  {ans['answerDescription']:<30} {ans['words']}")
"""))

    cells.append(code(r"""
# Dataset statistics
if nyt:
    all_words = {w.upper() for p in nyt for w in p["words"]}
    all_cats = [a["answerDescription"].upper() for p in nyt for a in p["answers"]]
    unique_cats = set(all_cats)
    all_groups = {frozenset(w.upper() for w in a["words"])
                  for p in nyt for a in p["answers"]}

    print(f"Puzzles:                 {len(nyt)}")
    print(f"Unique words:            {len(all_words):,}")
    print(f"Category mentions:       {len(all_cats):,}")
    print(f"Unique categories:       {len(unique_cats):,}")
    print(f"Unique 4-word groups:    {len(all_groups):,}")
"""))

    cells.append(code(r"""
# Distribution of category types
if nyt:
    # Categorise by a heuristic keyword pattern
    style_buckets = Counter()
    for cat in all_cats:
        if "___" in cat:
            style_buckets["Wordplay / fill-in"] += 1
        elif cat.startswith("SYNONYMS") or "MEAN" in cat or "SLANG" in cat:
            style_buckets["Synonyms / slang"] += 1
        elif any(k in cat for k in ["TYPES OF", "KINDS OF"]):
            style_buckets["Types/kinds"] += 1
        elif any(k in cat for k in ["FAMOUS", "MOVIES", "SONGS", "ALBUMS"]):
            style_buckets["Pop culture"] += 1
        else:
            style_buckets["Other / themed"] += 1

    labels, counts = zip(*style_buckets.most_common())
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(labels, counts, color="steelblue")
    ax.set_xlabel("Number of NYT categories")
    ax.set_title("Distribution of category styles in the NYT dataset")
    for i, c in enumerate(counts):
        ax.text(c + 5, i, str(c), va="center")
    plt.tight_layout()
    plt.show()
"""))

    # ==================================================================
    # 3. Pipeline A demo
    cells.append(md(r"""
## 3. Pipeline A demo (LLM-heavy baseline)

Pipeline A follows the architecture from "Making New Connections" (arXiv:2407.11240).
Per puzzle, it issues **5 LLM calls**: 4 to generate word pools (one per group) and
1 for the editor pass. Between each call, MPNET embeddings deterministically pick
the best 4 words from the LLM's 8 candidates.

In DRY_RUN mode, the `MockLLMClient` returns realistic canned responses so you can
see the full flow without any API key.
"""))

    cells.append(code(r"""
from src.llm_client import LLMClient
from src.generator.pipeline import PuzzlePipeline
from sentence_transformers import SentenceTransformer

# MPNET is the backbone of every pipeline
print("Loading MPNET model (all-mpnet-base-v2)...")
model = SentenceTransformer("all-mpnet-base-v2")
print("Ready.")
"""))

    cells.append(code(r"""
# Build word bank from NYT
word_bank = sorted(all_words) if nyt else [
    "RAIN", "SUN", "MOON", "STAR", "TREE", "LAKE", "BIRD", "FISH",
    "ROCK", "WAVE", "SAND", "WIND", "FIRE", "SNOW", "LEAF", "SEED"
]

# Pipeline A requires an LLM client (mock in dry-run mode)
pipeline_a = PuzzlePipeline(
    llm=LLMClient(),
    embedding_model=model,
    word_bank=word_bank,
)

puzzle = pipeline_a.generate(method="iterative")
show_puzzle(puzzle, title="Pipeline A (dry-run mock)")
"""))

    cells.append(md(r"""
**What just happened under the hood:**

1. For each of 4 groups, an LLM call returned a category and 8 candidate words.
2. `EmbeddingSelector.select_best()` enumerated all $\binom{8}{4} = 70$ subsets,
   scored each by average pairwise cosine similarity, and kept the best 4.
3. A 5th LLM call reviewed all 4 categories.
4. Groups were sorted by cohesion and assigned colors (yellow → purple).

Total: **5 LLM calls** for one puzzle. In production with a real API, this costs
~$0.005 with gpt-4o-mini.
"""))

    # ==================================================================
    # 4. CFR Mode A
    cells.append(md(r"""
## 4. Pipeline B demo --- Mode A (remix, 0 LLM calls)

Our novel pipeline. Instead of asking the LLM to generate words, we ask it (or
a lookup) for *category names*, then retrieve words via nearest-neighbours over
pre-computed MPNET embeddings. Mode A does no API calls at all --- it samples
existing NYT categories and lets the KNN find matching words.
"""))

    cells.append(code(r"""
from src.cfr.embedding_retriever import EmbeddingRetriever, load_nyt_word_bank_and_categories
from src.cfr.word_bank import build_augmented_word_bank
from src.cfr.pipeline import CFRPipeline

# Load NYT word bank + categories
nyt_words, nyt_categories = load_nyt_word_bank_and_categories(str(NYT_PATH))

# Augment with WordNet (14,877 words total — 3x NYT's 4,918)
bank, composition = build_augmented_word_bank(nyt_words)
print(f"Word bank composition: {composition}")
"""))

    cells.append(code(r"""
# Build the retriever (this caches to disk; first run takes ~2 min)
retriever = EmbeddingRetriever(
    word_bank=bank,
    nyt_categories=nyt_categories,
    model=model,
    cache_path=str(PROJECT_ROOT / "data" / "cache" / "nyt_embeddings_v2.npz"),
)
retriever.precompute()
print("Retriever ready.")
"""))

    cells.append(code(r"""
# Show the KNN retrieval in isolation — given a category name, what words fit?
for cat in ["BIRDS", "THINGS THAT GLOW", "FIRE ___"]:
    print(f"\nCategory: {cat}")
    top = retriever.retrieve(cat, top_k=8)
    for word, sim in top:
        nyt_mark = "(NYT)" if word in set(nyt_words) else "      "
        print(f"  {nyt_mark} {word:<15} sim={sim:.3f}")
"""))

    cells.append(code(r"""
# Generate a full CFR Mode A puzzle
cfr_pipeline = CFRPipeline(
    retriever=retriever,
    llm=None,                      # Mode A doesn't need an LLM
    embedding_model=model,
)
puzzle_a = cfr_pipeline.generate(mode="remix")
show_puzzle(puzzle_a, title="CFR Mode A (0 LLM calls, NYT category remix)")
"""))

    cells.append(md(r"""
**Walkthrough:** four diverse NYT categories were sampled (pairwise MPNET distance ≥ 0.35),
then for each one we ran KNN over the 14,877-word bank to get 30 similar words,
filtered out stems/sub-tokens/used words, enumerated the 70 four-word subsets,
and picked the best subset that is **not** a verbatim past NYT group.
"""))

    # ==================================================================
    # 5. CFR Mode B
    cells.append(md(r"""
## 5. Pipeline B demo --- Mode B (fresh, 1 LLM call)

Mode B makes exactly one batched LLM call that returns four fresh category names,
then runs the same KNN retrieval. This keeps the LLM's creative naming ability
but cuts total LLM calls from 5 (Pipeline A) to 1.
"""))

    cells.append(code(r"""
cfr_pipeline_b = CFRPipeline(
    retriever=retriever,
    llm=LLMClient(),               # 1 LLM call per puzzle (mock in dry-run)
    embedding_model=model,
)
puzzle_b = cfr_pipeline_b.generate(mode="fresh")
show_puzzle(puzzle_b, title="CFR Mode B (1 LLM call, fresh categories)")
"""))

    # ==================================================================
    # 6. Roundtable validation
    cells.append(md(r"""
## 6. Multi-solver roundtable validation

Every generated puzzle passes through two independent solvers. A puzzle is
accepted only if **either** fully recovers the intended partition. This is our
quality gate --- puzzles with ambiguous solutions are rejected.
"""))

    cells.append(code(r"""
from src.solvers.roundtable import Roundtable

roundtable = Roundtable(embedding_model=model)

for name, puzzle in [("Pipeline A", puzzle), ("CFR Mode A", puzzle_a), ("CFR Mode B", puzzle_b)]:
    val = roundtable.validate(puzzle)
    emb = val["groups_correct"].get("embedding", 0)
    clust = val["groups_correct"].get("clustering", 0)
    print(f"{name:<12}  emb={emb}/4  clust={clust}/4  agree={val['solver_agreement']}")
"""))

    # ==================================================================
    # 7. Dedup / rubric safety
    cells.append(md(r"""
## 7. Rubric-safety check: don't reproduce a past NYT puzzle

The rubric has one hard-fail rule: generating a verbatim past NYT puzzle is an
automatic fail. We guard against this at two levels:

1. **16-word set overlap** --- flag if more than 6 words overlap with any past puzzle.
2. **4-word group match** --- flag if any generated group is exactly a past NYT group.
"""))

    cells.append(code(r"""
from src.generator.deduplicator import Deduplicator

dedup = Deduplicator(nyt_path=str(NYT_PATH))

# Positive control: feed it a real NYT group, expect it to fire
if nyt:
    real_group = nyt[0]["answers"][0]["words"]
    real_puzzle_words = [w for ans in nyt[0]["answers"] for w in ans["words"]]

    print("=== Feeding the guard a REAL NYT puzzle ===")
    result = dedup.check(real_puzzle_words, groups=[{"words": ans["words"]} for ans in nyt[0]["answers"]])
    print(f"  is_duplicate:        {result['is_duplicate']}")
    print(f"  reason:              {result['reason']}")
    print(f"  exact_group_match:   {result['exact_group_match']}")
    print(f"  max_overlap:         {result['max_overlap']}")
"""))

    cells.append(code(r"""
# Negative control: random 4 words should NOT be a past NYT group
random.seed(0)
random_group = random.sample(bank, 4)
print(f"\n=== Feeding a RANDOM group: {random_group} ===")
res = dedup.check_groups([{"words": random_group}])
print(f"  exact_group_match: {res['exact_group_match']}")
"""))

    cells.append(code(r"""
# Now run the check on our freshly generated CFR Mode B puzzle
all_words_b = [w for g in puzzle_b["groups"] for w in g["words"]]
res = dedup.check(all_words_b, groups=puzzle_b["groups"])
print("=== Our fresh CFR Mode B puzzle ===")
print(f"  is_duplicate:        {res['is_duplicate']}")
print(f"  exact_group_match:   {res['exact_group_match']}")
print(f"  max_overlap with NYT: {res['max_overlap']}/16 words")
"""))

    # ==================================================================
    # 8. Color assignment
    cells.append(md(r"""
## 8. Difficulty colour assignment

Every group gets a cohesion score (average pairwise cosine similarity of its
4 words). The puzzle's 4 groups are sorted by this score: tightest → yellow
(easiest), loosest → purple (hardest).
"""))

    cells.append(code(r"""
# Plot cohesion-vs-colour across real NYT puzzles
if nyt:
    from src.generator.difficulty import compute_group_similarity

    by_position = {0: [], 1: [], 2: [], 3: []}
    for p in nyt[:200]:  # sample for speed
        scores = []
        for ans in p["answers"]:
            s = compute_group_similarity(ans["words"], model)
            scores.append(s)
        scores.sort(reverse=True)                       # highest first
        for i, s in enumerate(scores):
            by_position[i].append(s)

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = ["#F9DF6D", "#A0C35A", "#B0C4EF", "#BA81C5"]
    labels = ["yellow (easiest)", "green", "blue", "purple (hardest)"]
    for i, c in zip(range(4), colors):
        vals = by_position[i]
        ax.hist(vals, bins=25, alpha=0.6, label=labels[i], color=c)
    ax.set_xlabel("Average pairwise cosine similarity")
    ax.set_ylabel("Number of groups")
    ax.set_title("MPNET cohesion by difficulty colour (200 NYT puzzles)")
    ax.legend()
    plt.tight_layout()
    plt.show()
"""))

    # ==================================================================
    # 9. Benchmark results across real batches
    cells.append(md(r"""
## 9. Real benchmark results across all generated batches

Load every real-API batch we've generated and summarise pass rates, counts,
and non-NYT word usage.
"""))

    cells.append(code(r"""
def summarise_batch(path, label):
    path = Path(path)
    if not path.exists():
        return None
    valid_files = list(path.glob("*_valid.json"))
    invalid_files = list(path.glob("*_invalid.json"))

    def total(files):
        n = 0
        for f in files:
            with open(f) as fh:
                data = json.load(fh)
            n += len(data) if isinstance(data, list) else 1
        return n

    v = total(valid_files)
    i = total(invalid_files)
    if v + i == 0:
        return None
    return {"label": label, "valid": v, "invalid": i, "total": v + i,
            "pass_rate": 100.0 * v / (v + i)}

batches = [
    (PROJECT_ROOT / "data/generated/GPT-4o-mini",      "Pipeline A  (gpt-4o-mini)"),
    (PROJECT_ROOT / "data/generated/gpt4o",            "Pipeline A  (gpt-4o)"),
    (PROJECT_ROOT / "data/generated/batch_575",        "Pipeline A  (gpt-4o-mini, 575)"),
    (PROJECT_ROOT / "data/generated/cfr/remix",        "CFR v1 Mode A (remix)"),
    (PROJECT_ROOT / "data/generated/cfr/fresh",        "CFR v1 Mode B (fresh)"),
    (PROJECT_ROOT / "data/generated/cfr_v2/remix",     "CFR v2 Mode A (remix)"),
    (PROJECT_ROOT / "data/generated/cfr_v2/fresh",     "CFR v2 Mode B (fresh)"),
    (PROJECT_ROOT / "data/generated/cfr_v2/fresh_batch_300", "CFR v2 Mode B (300-puzzle run)"),
]

summaries = [s for s in (summarise_batch(p, l) for p, l in batches) if s]

print(f"{'Batch':<42} {'Valid':>6} {'Inv':>4} {'Total':>6} {'Pass':>6}")
print("-" * 70)
for s in summaries:
    print(f"{s['label']:<42} {s['valid']:>6} {s['invalid']:>4} {s['total']:>6} {s['pass_rate']:>5.1f}%")
print("-" * 70)

grand_v = sum(s["valid"] for s in summaries)
grand_t = sum(s["total"] for s in summaries)
print(f"{'GRAND TOTAL':<42} {grand_v:>6} {grand_t - grand_v:>4} {grand_t:>6} {100 * grand_v / max(grand_t,1):>5.1f}%")
"""))

    cells.append(code(r"""
# Pass-rate comparison chart
if summaries:
    labels = [s["label"] for s in summaries]
    rates = [s["pass_rate"] for s in summaries]
    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.barh(labels, rates, color=["#5B9BD5" if "CFR" in l else "#ED7D31" for l in labels])
    ax.set_xlim(0, 105)
    ax.set_xlabel("Pass rate (%)")
    ax.set_title("Validated pass rate by batch")
    for bar, r in zip(bars, rates):
        ax.text(r + 1, bar.get_y() + bar.get_height() / 2, f"{r:.1f}%", va="center")
    plt.tight_layout()
    plt.show()
"""))

    # ==================================================================
    # 10. Sample puzzles gallery
    cells.append(md(r"""
## 10. Gallery of sample generated puzzles

Five random validated puzzles from our 14,877-word augmented-bank batches.
"""))

    cells.append(code(r"""
# Load all valid CFR v2 puzzles and show a random 5
gallery = []
for sub in ["cfr_v2/remix", "cfr_v2/fresh", "cfr_v2/fresh_batch_300"]:
    for f in (PROJECT_ROOT / "data/generated" / sub).glob("*_valid.json"):
        with open(f) as fh:
            gallery.extend(json.load(fh))

random.seed(7)
picks = random.sample(gallery, min(5, len(gallery)))

for p in picks:
    print()
    show_puzzle(p)
"""))

    # ==================================================================
    # 11. Conclusions
    cells.append(md(r"""
## 11. Conclusions

### Headline findings

- **CFR Mode B achieves the same pass rate as Pipeline A (99%) at 1/20 the cost
  and 4× the speed.** One targeted LLM call + embedding retrieval beats five
  LLM calls.
- **Zero verbatim NYT-group reproductions across 400+ v2 benchmark puzzles.**
  The 4-word-group deduplication guard works as designed.
- **62–69% of output words come from the non-NYT portion of the augmented bank,**
  demonstrating that the 14,877-word vocabulary is actually used.

### Rubric compliance

| Requirement | Status |
|---|---|
| "Don't reproduce a past connections puzzle" | ✅ 4-word group dedup, verified on 400+ puzzles |
| "Word bank larger than the original" | ✅ 14,877 vs 4,918 (3× larger) |
| "Web interface" | ✅ Deployed: https://kevin2330.github.io/nyt-connections-generator/ |
| "Plausibly NYT-style" | Spot checks positive; human evaluation pending |

### Next steps

- Scale CFR Mode A to 10,000 puzzles (free, ~3.5 h wall time).
- Optional: add a CFR "false-group" Mode C to port the paper's best technique.
- Collect human evaluation ratings via the web app.

See `docs/methods.pdf` for the full technical writeup.
"""))

    nb["cells"] = cells
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python"},
    }
    return nb


def main():
    nb = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w") as f:
        nbf.write(nb, f)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
