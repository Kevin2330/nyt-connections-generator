# Infinite Connections

An AI system that generates, validates, and serves NYT-style Connections puzzles at scale using large language models and semantic embeddings.

---

<!--
Screenshot placeholder: replace the path below with an actual screenshot
of the web app once available (e.g., docs/images/webapp_screenshot.png).
-->

```
+------------------------------------------------------+
|             Infinite Connections                      |
|          AI-Generated Word Puzzles                    |
|                                                      |
|  +----------+ +----------+ +----------+ +----------+ |
|  |  SWIFT   | |  MARS    | |  POKER   | |  SALSA   | |
|  +----------+ +----------+ +----------+ +----------+ |
|  +----------+ +----------+ +----------+ +----------+ |
|  |  RAPID   | |  VENUS   | |  BRIDGE  | |  WALTZ   | |
|  +----------+ +----------+ +----------+ +----------+ |
|  +----------+ +----------+ +----------+ +----------+ |
|  |  FLEET   | |  SATURN  | |  HEARTS  | |  TANGO   | |
|  +----------+ +----------+ +----------+ +----------+ |
|  +----------+ +----------+ +----------+ +----------+ |
|  |  QUICK   | |  JUPITER | |  RUMMY   | |  BALLET  | |
|  +----------+ +----------+ +----------+ +----------+ |
|                                                      |
|          [ Shuffle ]  [ Deselect ]  [ Submit ]       |
+------------------------------------------------------+
```

---

## Quick Start

Everything runs out of the box in dry-run mode. No API keys are needed.

**0. Download the NYT dataset** (not included in the repo for copyright reasons)

Place the Connections dataset JSON file at:

```
data/nyt_puzzles/ConnectionsFinalDataset (1).json
```

The dataset contains 554 puzzles and is available from Kaggle. The pipeline
demo notebook and web app work without it (they use mock data), but the
data exploration notebook and solver benchmark require it.

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Run the test suite**

```bash
python -m pytest tests/ -v
```

All 31 tests should pass in under 15 seconds. Tests exercise the full
pipeline end-to-end: mock LLM generation, MPNET embedding selection,
solver validation, and quality metrics.

**3. Launch the web app**

```bash
python src/webapp/app.py
```

Open http://localhost:5000 in a browser. The app loads 5 pre-built puzzles
from `data/mock/mock_puzzles.json` and serves a playable Connections
interface with tile selection, color reveals, and mistake tracking.

**4. Open the notebooks**

```bash
jupyter notebook notebooks/
```

Two notebooks are available:

- `infinite_connections_demo.ipynb` -- End-to-end pipeline demonstration:
  puzzle generation, solver benchmarking, roundtable validation, and
  quality analysis. Runs fully in dry-run mode with mock LLM responses.

- `nyt_data_exploration.ipynb` -- Comprehensive analysis of 554 NYT
  Connections puzzles: word frequency, category types, difficulty trends,
  MPNET embedding distributions by color, and cross-puzzle patterns.

**5. Run the solver benchmark** (optional, takes ~9 minutes)

```bash
python scripts/benchmark_solvers.py
python scripts/plot_benchmark.py
```

Benchmarks the embedding and clustering solvers on all 554 NYT puzzles.
Results are saved to `data/solver_benchmark.json` and chart PNGs are
written to `data/`.

---

## Project Structure

```
infinite-connections/
|
|-- data/
|   |-- nyt_puzzles/              Ground truth: 554 NYT puzzles (JSON)
|   |-- generated/                Output directory for generated puzzles
|   |-- mock/                     Mock LLM responses for dry-run mode
|   |   +-- mock_puzzles.json     5 hand-crafted puzzles matching the schema
|   |-- solver_benchmark.json     Benchmark results (554 puzzles x 2 solvers)
|   +-- nyt_analysis_stats.json   Aggregate statistics from data exploration
|
|-- src/
|   |-- config.py                 Central configuration: DRY_RUN, paths, thresholds
|   |-- llm_client.py             LLM abstraction (Anthropic API + MockLLMClient)
|   |
|   |-- generator/                Puzzle generation pipeline
|   |   |-- pipeline.py           Main orchestrator (iterative + false-group methods)
|   |   |-- group_creator.py      LLM calls + MPNET embedding selection (8 -> 4 words)
|   |   |-- puzzle_editor.py      Second-pass LLM review of category names
|   |   |-- difficulty.py         Color assignment via cosine similarity thresholds
|   |   |-- deduplicator.py       Overlap check against NYT ground truth
|   |   +-- prompts.py            All prompt templates
|   |
|   |-- solvers/                  Multiple independent solver implementations
|   |   |-- embedding_solver.py   Greedy C(16,4) enumeration by cosine similarity
|   |   |-- clustering_solver.py  Group-Penalty scoring with beam search (width=10)
|   |   |-- llm_solver.py         Claude chain-of-thought solver
|   |   +-- roundtable.py         Multi-solver convergence validator
|   |
|   |-- evaluation/               Quality metrics and analysis
|   |   |-- metrics.py            Group Similarity Score, Penalty Score
|   |   +-- analyzer.py           Dataset statistics, NYT comparison
|   |
|   +-- webapp/                   Playable web interface
|       |-- app.py                Flask backend (puzzle API)
|       |-- templates/index.html  Game page
|       +-- static/               CSS and JavaScript (game.js, style.css)
|
|-- notebooks/
|   |-- infinite_connections_demo.ipynb    Pipeline demo (primary deliverable)
|   +-- nyt_data_exploration.ipynb         NYT dataset analysis
|
|-- scripts/
|   |-- benchmark_solvers.py      Run solvers on all 554 NYT puzzles
|   +-- plot_benchmark.py         Generate accuracy charts from benchmark results
|
|-- tests/
|   +-- test_pipeline.py          31 tests covering all modules end-to-end
|
|-- docs/
|   |-- executive_summary.md      2-page non-technical summary
|   |-- faq.md                    Anticipated questions and answers
|   +-- technical_appendix.md     Algorithms, formulas, architecture diagram
|
|-- papers/                       Reference PDFs (read-only)
|-- repos/                        Cloned reference repos (read-only)
|-- resources/                    Blog posts and web references
|-- requirements.txt
+-- README.md
```

---

## How It Works

The project has three workstreams.

### 1. Puzzle Generation Pipeline

Each puzzle is built through a multi-step pipeline:

1. **Group creation** -- An LLM (Claude) proposes a category name and 8
   candidate words. Story injection (random seed words from the NYT word
   bank) prevents repetitive output.

2. **Embedding selection** -- MPNET (`all-mpnet-base-v2`) computes pairwise
   cosine similarity across all C(8,4)=70 subsets. The most internally
   cohesive 4 words are selected, replacing unreliable LLM self-selection.

3. **Iteration** -- Steps 1-2 repeat 4 times, with previous groups passed as
   context to avoid word reuse.

4. **Editor pass** -- A second LLM call reviews the complete puzzle and
   rewrites any inaccurate category names.

5. **Difficulty assignment** -- Groups are ranked by cosine similarity and
   mapped to colors: highest similarity = yellow (easiest), lowest = purple
   (hardest). Thresholds are calibrated against empirical NYT data.

6. **Deduplication** -- The 16-word set is checked against all 554 known NYT
   puzzles. Puzzles with more than 6 overlapping words are flagged.

The **false-group method** is an alternative that produces higher-quality
puzzles: a decoy group is generated first, then each of its 4 words is
reinterpreted via an alternate meaning to seed 4 real groups. The decoy
becomes a trap for solvers.

### 2. Multi-Solver Validation

A valid puzzle must have exactly one correct solution. Three independent
solvers check this:

| Solver | Method | Speed |
|--------|--------|-------|
| Embedding | Greedy selection by highest pairwise cosine similarity | Fast (50 puzzles/s) |
| Clustering | Group-Penalty scoring with beam search (G = 0.4I + 0.3s + 0.3V) | Medium (1 puzzle/s) |
| LLM | Claude chain-of-thought reasoning | Slow (API-bound) |

The **Roundtable Validator** runs the embedding and clustering solvers on
every candidate puzzle. If both converge to the same 4 groups and those
groups match the intended answer, the puzzle is accepted. Disagreement
means the puzzle is ambiguous.

### 3. Deliverables

- **Jupyter notebook** -- Reproducible pipeline demo with live generation,
  solver benchmarking, and quality visualizations.
- **Web app** -- Playable Connections interface with a 4x4 word grid, color
  reveals, "one away" feedback, and 4-mistake limit.
- **Written reports** -- Executive summary, FAQ, and technical appendix in
  `docs/`.

---

## Generating Real Puzzles

By default, `DRY_RUN=true` and all LLM calls return mock responses. To
generate real puzzles with live API calls:

### Using the Anthropic API (Claude)

```bash
export DRY_RUN=false
export ANTHROPIC_API_KEY=sk-ant-...
```

The pipeline uses `claude-sonnet-4-20250514` for both generation and the
editor pass.

### Using the OpenAI API (GPT-4o-mini)

```bash
export DRY_RUN=false
export LLM_PROVIDER=openai
export LLM_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...
```

GPT-4o-mini is recommended for bulk generation due to lower cost.

### Cost estimates

| Provider | Model | Cost per puzzle | 100 puzzles | 10,000 puzzles |
|----------|-------|----------------|-------------|----------------|
| OpenAI | gpt-4o-mini | ~$0.002 | ~$0.21 | ~$21 |
| Anthropic | claude-sonnet-4-20250514 | ~$0.04 | ~$4 | ~$400 |

### Recommended workflow

```bash
# Start small: generate 10 candidates, expect ~4 valid
python -c "
from src.generator.pipeline import PuzzlePipeline
pipeline = PuzzlePipeline()
puzzles = pipeline.generate_batch(10, method='false_group')
print(f'Generated {len(puzzles)} puzzles')
"

# Scale up once quality looks good
# Target: 100 candidates -> ~40 valid puzzles
```

Each candidate puzzle goes through the editor pass and deduplication
automatically. Run the Roundtable Validator separately to filter for
uniqueness:

```python
from src.solvers.roundtable import Roundtable

roundtable = Roundtable(embedding_model=model)
for puzzle in puzzles:
    result = roundtable.validate(puzzle)
    if result["valid"]:
        # Save to data/generated/
        ...
```

---

## Key References

### Papers

1. **Making New Connections** (arXiv:2407.11240) -- Generation pipeline
   architecture, story injection, false-group method. Primary reference for
   the generator.

2. **Missed Connections** (arXiv:2404.11730) -- Embedding solver and LLM
   solver baselines. Source of the greedy cosine-similarity approach and
   chain-of-thought prompting strategy.

3. **Deceptively Simple** (arXiv:2412.01621) -- Group Similarity Score
   formula (G = 0.4I + 0.3s + 0.3V), Penalty Score, and beam search solver.

4. **Connecting the Dots** (arXiv:2406.11012) -- Category knowledge taxonomy
   and human evaluation methodology.

### Data

- NYT Connections dataset: 554 puzzles from the
  [Connections Kaggle dataset](https://www.kaggle.com/datasets),
  stored at `data/nyt_puzzles/ConnectionsFinalDataset (1).json`.

### Code references

- `repos/NLP-Connections/` -- Solver implementation patterns.
- `repos/react-connections-game/` -- Frontend UI design reference.
- `resources/merrill_solver_blog.html` -- Practical solver walkthrough.

---

## Team

| Name | Role |
|------|------|
| [Team Member 1] | Pipeline architecture, puzzle generation |
| [Team Member 2] | Solver implementation, benchmarking |
| [Team Member 3] | Web app, notebook, evaluation |

---

Built for **STA 561D** at Duke University.
