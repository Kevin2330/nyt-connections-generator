# Infinite Connections — Technical Appendix

## Architecture

```
User Request
    │
    ▼
┌─────────────────────────────────────────────────┐
│              PuzzlePipeline                      │
│                                                  │
│  ┌──────────────┐   ┌──────────────────────┐    │
│  │ GroupCreator  │──▶│ EmbeddingSelector    │    │
│  │ (Claude API)  │   │ (MPNET: 8 → 4 words)│    │
│  └──────────────┘   └──────────────────────┘    │
│         │                                        │
│         ▼                                        │
│  ┌──────────────┐                                │
│  │ PuzzleEditor │  (second Claude pass)          │
│  └──────────────┘                                │
│         │                                        │
│         ▼                                        │
│  ┌──────────────┐   ┌──────────────────────┐    │
│  │ Difficulty   │──▶│ Color Assignment     │    │
│  │ (cosine sim) │   │ (yellow→purple)      │    │
│  └──────────────┘   └──────────────────────┘    │
│         │                                        │
│         ▼                                        │
│  ┌──────────────┐                                │
│  │ Deduplicator │  (check vs 554 NYT puzzles)   │
│  └──────────────┘                                │
└─────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────┐
│              Roundtable Validator                 │
│                                                  │
│  ┌──────────────┐  ┌──────────────────────┐     │
│  │ Embedding    │  │ Clustering Solver    │     │
│  │ Solver       │  │ (beam search, G-P)   │     │
│  └──────────────┘  └──────────────────────┘     │
│         │                    │                    │
│         └────────┬───────────┘                    │
│                  ▼                                │
│          Convergence Check                       │
│      (agree? → VALID / INVALID)                  │
└─────────────────────────────────────────────────┘
```

## Algorithms

### Group Similarity Score (from "Deceptively Simple" paper)

For a group of 4 word embeddings E = {e₁, e₂, e₃, e₄}:

```
G = 0.4·I + 0.3·s + 0.3·V

where:
  I = -K(E)           # negative k-means inertia (k=1)
  s = min(P)           # minimum pairwise cosine similarity
  V = mean(P)/(1+var(P))  # stability-weighted mean similarity
  P = {cos(eᵢ, eⱼ) : i < j}  # all pairwise similarities
```

### Penalty Score

For a candidate group C with remaining words R:

```
P = (1/|R|) · Σᵣ cos(μ_C, r)

where μ_C is the centroid of group C's embeddings
```

### Beam Search

The clustering solver uses beam search (width=10) to find the optimal partition:

1. Initialize beam with empty grouping
2. For each of 4 steps:
   - Enumerate all C(|remaining|, 4) possible next groups
   - Score each: cumulative_score += G - P
   - Keep top-10 candidates
3. Return highest-scoring complete partition

### Difficulty Color Thresholds

Empirically calibrated from NYT data (Table 1, "Making New Connections"):

| Color  | Avg Cosine Similarity | Variance |
|--------|----------------------|----------|
| Yellow | ~0.40                | 0.0285   |
| Green  | ~0.35                | 0.0214   |
| Blue   | ~0.29                | 0.0123   |
| Purple | ~0.27                | 0.0108   |

## Key Implementation Details

### Story Injection

To avoid repetitive LLM outputs, each group generation call includes:

> "First, write a short story using these words: [4 random words from NYT word bank]. Then use that story as inspiration for creating your category."

This dramatically increases category diversity by seeding the LLM with random context.

### False Group Pipeline

1. Generate root group: 4 words with multiple meanings (e.g., BALL, GLOBE, RING, WHEEL → "THINGS THAT ARE ROUND")
2. For each root word, identify an alternate meaning (BALL → "formal dance event")
3. Generate a new category inspired by each alternate meaning
4. The 4 new categories become the puzzle; the root group is a decoy

### Deduplication

Each generated puzzle's 16-word set is compared against all 554 NYT puzzles. A puzzle is flagged if more than 6 words overlap with any single NYT puzzle.

## References

1. "Making New Connections" (arXiv:2407.11240) — Generation pipeline
2. "Missed Connections" (arXiv:2404.11730) — Solver baselines
3. "Deceptively Simple" (arXiv:2412.01621) — Scoring formulas
4. "Connecting the Dots" (arXiv:2406.11012) — Category taxonomy

---

*STA 561D — Duke University*
