# Infinite Connections — FAQ

## General

### Q: What is NYT Connections?

A daily word puzzle by the New York Times where players sort 16 words into 4 groups of 4, each sharing a hidden connection. Groups are color-coded by difficulty: yellow (easiest) through purple (hardest). Players get 4 mistakes before losing.

### Q: Why is puzzle generation hard?

Three core challenges: (1) ensuring exactly one valid solution among 2.6M+ possible groupings, (2) calibrating difficulty across 4 levels, and (3) including plausible-but-wrong "false groups" that make the puzzle engaging.

### Q: How does this differ from random word grouping?

Random groupings almost never produce valid puzzles. Our pipeline uses semantic embeddings to ensure groups are internally cohesive (words relate to each other) while being externally distinct (words don't fit in other groups). The false-group method intentionally adds deception.

## Technical

### Q: Why use MPNET instead of the LLM for word selection?

LLMs are inconsistent at estimating semantic similarity between words. When asked to pick "the 4 most related words from 8," Claude produces different selections at different temperatures and often picks words that are thematically interesting but not maximally cohesive. MPNET cosine similarity is deterministic and correlates well with human difficulty perception.

### Q: What is the false-group pipeline?

The most effective generation method: (1) generate a "root group" of 4 words with multiple meanings, (2) for each root word, generate a new category based on its alternate meaning, (3) the 4 new categories become the puzzle; the root group is a decoy. This naturally creates deceptive overlaps.

### Q: How does multi-solver validation work?

Two independent solvers (embedding greedy + clustering beam search) attempt each puzzle. If both find the same 4 groups AND those groups match the intended answer, the puzzle passes. Disagreement indicates ambiguity — the puzzle could be interpreted multiple ways.

### Q: What embedding model do you use?

`all-mpnet-base-v2` from the sentence-transformers library. This model maps words/phrases to 768-dimensional vectors where cosine similarity correlates with semantic relatedness.

### Q: How are difficulty colors assigned?

Groups are sorted by average pairwise cosine similarity: highest similarity = yellow (easiest, words are obviously related), lowest = purple (hardest, connection is subtle). Thresholds are calibrated against empirical NYT data.

## Evaluation

### Q: What are the solver accuracy baselines?

From the reference papers: MPNET embedding solver achieves ~11.6% full-puzzle solve rate on NYT puzzles. GPT-4 with chain-of-thought achieves ~38.9%. Our solvers target similar ranges.

### Q: How do you measure puzzle quality?

Multiple metrics: (1) solver convergence rate (do independent solvers agree?), (2) cosine similarity distribution by color (does it match NYT patterns?), (3) category diversity (unique category names), (4) deduplication (no overlap with existing puzzles).

### Q: What percentage of generated puzzles are valid?

In our experiments, approximately 40% of candidate puzzles pass multi-solver validation. The false-group method has a higher pass rate than iterative generation.

## Reproducibility

### Q: How do I run this without an API key?

Set `DRY_RUN=true` (the default). The system uses a mock LLM client that returns realistic pre-built responses, exercising all code paths including MPNET embedding selection.

### Q: What are the compute requirements?

The MPNET model requires ~400MB of RAM. Puzzle generation (with real API) costs approximately $0.001-0.003 per puzzle using Claude Sonnet. The embedding model runs on CPU.

---

*STA 561D — Duke University*
