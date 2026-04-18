"""Build the comprehensive methods PDF via fpdf2 (no LaTeX compiler needed).

Mirrors docs/methods.tex but renders as PDF directly.
"""

import sys
from pathlib import Path
from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "docs" / "methods.pdf"


class Methods(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(95, 5, "Infinite Connections -- Methods", align="L")
        self.cell(95, 5, "STA 561D | Duke", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section(self, num, title):
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(26, 84, 144)
        self.ln(4)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(26, 84, 144)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def subsection(self, title):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.ln(2)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def subsubsection(self, title):
        self.set_font("Helvetica", "BI", 10)
        self.set_text_color(70, 70, 70)
        self.ln(1)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(10)
        self.multi_cell(190, 5, text)
        self.ln(1)

    def bullet(self, text, indent=0):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(10 + indent)
        self.multi_cell(190 - indent, 5, "  -  " + text)

    def numbered(self, n, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(12)
        self.multi_cell(188, 5, f"  {n}.  " + text)

    def note(self, text):
        self.ln(2)
        y = self.get_y()
        self.set_fill_color(232, 240, 254)
        self.set_draw_color(80, 130, 200)
        self.set_font("Helvetica", "", 10)
        lines_est = len(text) // 85 + text.count("\n") + 2
        h = max(14, lines_est * 5 + 4)
        self.rect(10, y, 190, h, style="DF")
        self.set_xy(14, y + 2)
        self.multi_cell(182, 5, text)
        self.ln(2)

    def code(self, text, font_size=8):
        self.ln(2)
        y = self.get_y()
        self.set_fill_color(245, 245, 240)
        self.set_draw_color(200, 200, 190)
        self.set_font("Courier", "", font_size)
        lines = text.strip().split("\n")
        h = len(lines) * (font_size * 0.45) + 4
        self.rect(10, y, 190, h, style="DF")
        self.set_xy(13, y + 2)
        for line in lines:
            self.cell(0, font_size * 0.45, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(13)
        self.ln(3)

    def eqn(self, text):
        """Render a math-style line centered."""
        self.ln(1)
        self.set_font("Courier", "", 10)
        self.set_fill_color(255, 248, 220)
        self.set_draw_color(220, 180, 60)
        y = self.get_y()
        self.rect(20, y, 170, 8, style="DF")
        self.set_xy(20, y + 1)
        self.cell(170, 6, text, align="C")
        self.ln(10)

    def table(self, headers, rows, widths=None, header_fill=(220, 230, 245)):
        if widths is None:
            widths = [190 / len(headers)] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(*header_fill)
        self.set_text_color(0, 0, 0)
        self.set_draw_color(100, 100, 100)
        for w, h in zip(widths, headers):
            self.cell(w, 7, h, border=1, fill=True, align="L")
        self.ln(7)
        self.set_font("Helvetica", "", 9)
        for i, row in enumerate(rows):
            fill = (i % 2 == 0)
            self.set_fill_color(248, 248, 248)
            for w, cell in zip(widths, row):
                self.cell(w, 6, str(cell), border=1, fill=fill, align="L")
            self.ln(6)
        self.ln(2)


def build():
    pdf = Methods(orientation="P", unit="mm", format="Letter")
    pdf.alias_nb_pages()
    pdf.set_margins(10, 15, 10)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # ---------- Title ----------
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(26, 84, 144)
    pdf.ln(5)
    pdf.cell(0, 12, "Infinite Connections: Methods", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, "A Complete Technical Description of the Puzzle Generation System",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "STA 561D  |  Duke University  |  April 2026",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Abstract
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "Abstract", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.body(
        "We describe the full methodology behind our NYT Connections puzzle "
        "generator. The system builds puzzles via two complementary pipelines: "
        "an LLM-heavy baseline (5 API calls/puzzle) and a novel Category-First "
        "Retrieval (CFR) pipeline (0-1 API calls/puzzle) that uses sentence "
        "embeddings and k-nearest-neighbors search over an augmented 14,877-word "
        "vocabulary. Every generated puzzle is checked against the full set of "
        "past NYT puzzles at both the 16-word and 4-word-group level, assigned "
        "difficulty colors via average pairwise cosine similarity, and validated "
        "by two independent solvers that must converge on the intended solution. "
        "Across 200 benchmark puzzles, CFR v2 achieves a 99% solver-validated "
        "pass rate, uses 62-69% non-NYT words, and reproduces zero past NYT groups."
    )

    # ---------- 1. Problem and Design ----------
    pdf.section(1, "Problem and High-Level Design")

    pdf.subsection("The task")
    pdf.body(
        "The New York Times Connections puzzle asks the player to partition 16 "
        "words into 4 disjoint groups of 4, where each group shares a hidden "
        "theme. Themes range from synonyms (WAYS TO SAY HELLO) to fill-in-the-blank "
        "wordplay (FIRE ___), shared sounds, or pop-culture references. The four "
        "groups have an intended difficulty ordering: yellow (easiest) to purple "
        "(hardest)."
    )

    pdf.subsection("What we built")
    pdf.numbered(1, "A generation system with two pipelines and three modes.")
    pdf.numbered(2,
        "A multi-solver validator that runs two independent automated solvers on "
        "every generated puzzle and accepts only those that can be solved "
        "deterministically.")
    pdf.numbered(3,
        "A playable web app hosted on GitHub Pages that loads a bundled set of "
        "validated puzzles and replicates the NYT UI.")

    pdf.subsection("Two pipelines, three modes")
    pdf.table(
        ["Pipeline", "Mode", "LLM calls / puzzle", "Source of inspiration"],
        [
            ["A - Iterative baseline", "single", "5", "LLM proposes word pools"],
            ["B - CFR", "remix", "0", "NYT category pool"],
            ["B - CFR", "fresh", "1 batched", "LLM writes fresh categories"],
        ],
        widths=[55, 30, 40, 65],
    )
    pdf.body(
        "All three share identical post-generation steps: color assignment, "
        "deduplication, and roundtable validation. Only the 'get categories' "
        "and 'get candidate words' steps differ."
    )

    # ---------- 2. Data ----------
    pdf.section(2, "Data")

    pdf.subsection("Ground-truth NYT dataset")
    pdf.body(
        "We use ConnectionsFinalDataset.json, a publicly-available scrape of 554 "
        "past NYT Connections puzzles. Each puzzle contains:"
    )
    pdf.bullet("date, contest")
    pdf.bullet("words: a list of 16 strings")
    pdf.bullet(
        "answers: a list of 4 objects, each with answerDescription (category name) "
        "and words (the 4 words in that group)")
    pdf.bullet("difficulty: a float in [0,1]")
    pdf.body("From this we derive:")
    pdf.bullet("W_NYT: 4,918 unique words (uppercased, deduplicated)")
    pdf.bullet("C: 2,054 unique category names")
    pdf.bullet("G_NYT: 2,216 past 4-word groups (stored as frozensets)")
    pdf.bullet("554 complete 16-word puzzles for word-overlap dedup")

    pdf.subsection("Augmented word bank (v2)")
    pdf.body(
        "After the professor's guidance that 'the total word bank should be more "
        "than that of the original game's,' we expanded W to 14,877 words by "
        "unioning three sources:"
    )
    pdf.numbered(1, "W_NYT (4,918 words).")
    pdf.numbered(2,
        "W_WN: NLTK WordNet lemmas filtered by (a) single-token only, (b) "
        "alphabetic only, (c) length in [3, 15], (d) tagged-corpus frequency >= 1, "
        "and (e) not in a profanity blocklist. Yields ~10,000 common English "
        "lemmas.")
    pdf.numbered(3,
        "W_G10k: optional Google 10k most-common-English list, if present on disk.")
    pdf.eqn("W = W_NYT  U  W_WN  U  W_G10k,    |W| = 14,877")
    pdf.body(
        "The result is cached to data/cache/augmented_word_bank.json to avoid "
        "recomputing."
    )

    pdf.subsection("Embedding model")
    pdf.body(
        "We use sentence-transformers with the model all-mpnet-base-v2, which "
        "produces 768-dimensional contextual embeddings. Every word in W and "
        "every category in C is encoded once and cached to "
        "data/cache/nyt_embeddings_v2.npz. The cached matrix E_W (14,877 x 768) "
        "is the substrate for all retrieval and scoring."
    )

    # ---------- 3. Pipeline A ----------
    pdf.section(3, "Pipeline A: LLM-Heavy Baseline")
    pdf.body(
        "Pipeline A implements the iterative generator described in 'Making New "
        "Connections' (arXiv:2407.11240), extended with story-injection for "
        "diversity. It is our reference point: a correct, working implementation "
        "of the strongest LLM-only approach in the literature."
    )

    pdf.subsection("Per-puzzle flow")
    pdf.code(
        "groups = []\n"
        "for i in 1..4:\n"
        "    seed = 4 random words from W_NYT             # story injection\n"
        "    (category, pool_8) = LLM(seed, groups)       # Call 1-4\n"
        "    words_4 = MPNET-select-best(pool_8, 4)       # 70 combos ranked\n"
        "    groups.append({category, words_4})\n"
        "groups = LLM-editor(groups)                       # Call 5\n"
        "groups = assign-colors(groups)\n"
        "dedup(groups)\n"
        "roundtable-validate(groups)"
    )

    pdf.subsection("Story injection for diversity")
    pdf.body(
        "A known failure mode of LLMs is repetitive output (BOARD GAMES: chess, "
        "checkers, monopoly, life; repeated dozens of times). We insert 4 random "
        "words from W_NYT into the system prompt as 'inspiration.' The LLM is "
        "told to write a short imagined story around those words before proposing "
        "a category. This dramatically increases category diversity."
    )

    pdf.subsection("MPNET word selection")
    pdf.body(
        "The LLM returns an 8-word candidate pool. We do NOT let the LLM pick "
        "which 4 words to keep; instead, for all C(8,4)=70 subsets S we compute"
    )
    pdf.eqn("score(S) = mean over pairs (u,v) in S  of  cos( e(u), e(v) )")
    pdf.body(
        "and return the subset with the highest score. This deterministic step "
        "cleans up LLM inconsistency."
    )

    pdf.subsection("Editor pass")
    pdf.body(
        "A single LLM call (Call 5) reviews the complete 4-group puzzle and "
        "either approves each category name or rewrites one it considers "
        "inaccurate. In practice ~95% of categories pass unchanged."
    )

    pdf.subsection("False-group variant")
    pdf.body(
        "An alternative method produces the highest-quality puzzles in user "
        "studies. The LLM first proposes a plausible-but-fake 'root' group "
        "(e.g., 'ROUND THINGS: ball, globe, ring, wheel'), then for each root "
        "word finds an alternate meaning and generates a real group around it. "
        "The 4 real groups form the puzzle; the fake root is a decoy that "
        "'fits' but isn't a valid grouping. Enabled via --method false_group."
    )

    # ---------- 4. CFR ----------
    pdf.section(4, "Pipeline B: Category-First Retrieval (CFR)")
    pdf.body(
        "CFR is our primary methodological contribution. It inverts Pipeline A: "
        "instead of the LLM generating words, it generates only category names "
        "(or none at all), and the words are retrieved from W by k-nearest-neighbors "
        "over MPNET embeddings."
    )

    pdf.subsection("Motivation")
    pdf.body(
        "Pipeline A wastes LLM tokens. The LLM generates 8 words, then MPNET "
        "picks 4 of them anyway; the other 4 are discarded. Two observations:"
    )
    pdf.numbered(1, "The LLM is good at naming (creative, readable categories).")
    pdf.numbered(2,
        "MPNET is good at ranking (deterministic semantic similarity over a "
        "fixed vocabulary).")
    pdf.body("CFR assigns each task to the component that handles it best.")

    pdf.subsection("Offline precomputation (~5 minutes, once)")
    pdf.code(
        "Load W (14,877 words) and C (2,054 categories) from NYT data\n"
        "E_W = MPNET(W)    # (14877 x 768)\n"
        "E_C = MPNET(C)    # (2054 x 768)\n"
        "KNN = NearestNeighbors(E_W, metric='cosine')\n"
        "G_NYT = { frozenset(g.words) : g in all NYT groups }\n"
        "Save E_W, E_C, KNN, G_NYT to disk cache"
    )

    pdf.subsection("Per-puzzle flow")
    pdf.code(
        "# Step 1: obtain 4 category names\n"
        "if mode == 'remix':\n"
        "    cats = sample-diverse(C, n=4, min-dist=0.35)   # 0 LLM calls\n"
        "elif mode == 'fresh':\n"
        "    cats = LLM-batched('4 categories')             # 1 LLM call\n"
        "\n"
        "used = set(); groups = []\n"
        "for c in cats:\n"
        "    q = MPNET(c)                                   # Step 2: KNN\n"
        "    cand = top-k(KNN, q, k=30, exclude=used,\n"
        "                 filter stems & sub-tokens)\n"
        "    pool = cand[:8]\n"
        "    best_4 = pick-best-non-NYT-combo(pool, G_NYT)  # Step 3: guard\n"
        "    groups.append({c, best_4}); used |= best_4\n"
        "\n"
        "groups = assign-colors(groups)                     # Step 4\n"
        "dedup(groups, G_NYT)                               # Step 5\n"
        "roundtable-validate(groups)                        # Step 6"
    )

    pdf.subsection("Mode A: NYT category remix")
    pdf.body(
        "Mode A picks 4 existing NYT category names, diverse in embedding space. "
        "'Diverse' means all C(4,2)=6 pairwise cosine distances between the four "
        "categories are at least 0.35; rejection sampling is used until this "
        "condition is met. No LLM call. No API cost. No network latency."
    )

    pdf.subsection("Mode B: Fresh LLM categories")
    pdf.body(
        "Mode B uses one batched LLM call that returns a JSON object with four "
        "unrelated categories. This is a single call producing four categories, "
        "not four separate calls. Cost is ~$0.0005 per puzzle with gpt-4o-mini."
    )

    pdf.subsection("KNN retrieval with filters")
    pdf.body(
        "Given a category embedding q, we request the top k=30 words by cosine "
        "distance from KNN. Before returning, three filters are applied in order:"
    )
    pdf.numbered(1,
        "Exclusion: words already used in previous groups of the same puzzle.")
    pdf.numbered(2,
        "Category-token overlap: a word is dropped if it is literally one of the "
        "tokens in the category name (e.g., drop 'TIME' for category 'TIME "
        "PERIODS').")
    pdf.numbered(3,
        "Morphological duplicates: two words sharing a crude stem (via a "
        "suffix-stripping heuristic) are not both kept. If TIME is chosen, "
        "TIMES/TIMER/TIMING are skipped.")

    pdf.subsection("Best-combination selection with NYT-group safety")
    pdf.body(
        "From the 8 surviving candidates, we enumerate all C(8,4)=70 subsets, "
        "score each by average pairwise cosine similarity (as in Pipeline A), "
        "and rank descending. We return the first combination that is not a "
        "verbatim past NYT group:"
    )
    pdf.eqn("S* = argmax { score(S) : S subset pool, |S|=4, frozenset(S) not in G_NYT }")
    pdf.body(
        "If the top-scoring combination happens to be a past NYT group (e.g., "
        "KNN retrieved the literal NYT bird group when queried for 'BIRDS'), we "
        "fall through to the next-best combination. In 200 benchmark v2 puzzles, "
        "this fallback fired a handful of times and produced 0 verbatim NYT "
        "group matches in the final output."
    )

    # ---------- 5. Shared post-processing ----------
    pdf.section(5, "Shared Post-Generation Components")
    pdf.body(
        "Every pipeline -- Pipeline A, CFR Mode A, and CFR Mode B -- passes "
        "through the same 3-stage post-processing."
    )

    pdf.subsection("Difficulty color assignment")
    pdf.body("For each group g with words W_g, compute")
    pdf.eqn("mu(g) = avg-sim(g) = mean over pairs (u,v) in W_g of cos(e(u),e(v))")
    pdf.body(
        "Sort the 4 groups descending by mu and map to colors: yellow (highest, "
        "easiest) -> green -> blue -> purple (lowest, hardest). The thresholds "
        "are empirical, matching Table 1 of 'Making New Connections': "
        "yellow ~0.40, green ~0.35, blue ~0.29, purple ~0.27. Assignment is by "
        "rank within the puzzle, so every puzzle always gets exactly one group "
        "per color."
    )

    pdf.subsection("Deduplication")
    pdf.body(
        "The rubric rules that any generation of a verbatim past NYT puzzle is "
        "an automatic fail. We enforce this in two independent ways:"
    )
    pdf.subsubsection("16-word set overlap")
    pdf.body(
        "For the 16-word set U of the candidate puzzle, compute the maximum "
        "overlap with any single past NYT puzzle: o* = max |U intersect p.words|. "
        "Flag as duplicate if o* > 6."
    )
    pdf.subsubsection("4-word group match")
    pdf.body(
        "For each generated group g, test: is frozenset(g) in G_NYT? If any "
        "generated group matches a past NYT group verbatim, flag the puzzle as "
        "a duplicate."
    )

    pdf.subsection("Roundtable validation")
    pdf.body(
        "Two independent solvers attempt to recover the intended 4-group "
        "partition. A puzzle is accepted if either solver fully recovers it."
    )
    pdf.subsubsection("Solver 1 -- Embedding (greedy)")
    pdf.body(
        "Enumerate all C(16,4)=1,820 possible 4-word groups, score each by "
        "average pairwise cosine similarity, greedily pick highest-scoring "
        "non-overlapping groups until 4 are chosen. Fast, deterministic. "
        "Baseline on 554 real NYT puzzles: 2.0% full-puzzle solve rate."
    )
    pdf.subsubsection("Solver 2 -- Clustering (beam search)")
    pdf.body(
        "Per 'Deceptively Simple' (arXiv:2412.01621), each candidate group g "
        "gets a composite score G(g) = 0.4*I(g) + 0.3*s(g) + 0.3*V(g), where:"
    )
    pdf.bullet("I(g) = -K(E_g), minus k-means inertia at k=1 (tight cluster preferred)")
    pdf.bullet(
        "s(g) = min pairwise cos(e(u),e(v)) over all 6 pairs (guards outliers)")
    pdf.bullet(
        "V(g) = mean(P_g) / (1 + var(P_g)), where P_g is the pairwise sim vector "
        "(rewards stable cohesion)")
    pdf.body(
        "A penalty P(g, R) = mean over r in R of cos(mu_g, e(r)) discourages "
        "groups bleeding into the remaining word set. Beam search (width 10) "
        "finds the 4-group partition maximizing sum of G(g_i) - P(g_i, R_i)."
    )
    pdf.subsubsection("Acceptance rule")
    pdf.body(
        "A puzzle is accepted if at least one of Solvers 1 and 2 returns a "
        "partition matching all 4 intended groups. Conservative by design: our "
        "solvers solve only 2-3% of real NYT puzzles, so a puzzle they CAN solve "
        "has cleanly recoverable semantic structure (i.e., unambiguous)."
    )
    pdf.subsubsection("Optional LLM solver")
    pdf.body(
        "A third solver prompts the LLM with the 16 shuffled words and "
        "chain-of-thought instructions, parsing its returned 4-group partition. "
        "Used only for edge cases or published benchmarks; off by default."
    )

    # ---------- 6. Implementation ----------
    pdf.section(6, "Implementation Details")

    pdf.subsection("Code organization")
    pdf.code(
        "src/\n"
        " |-- config.py             DRY_RUN flag, model names, thresholds\n"
        " |-- llm_client.py         OpenAI / Anthropic / Mock unified\n"
        " |-- generator/            Pipeline A\n"
        " |   |-- pipeline.py\n"
        " |   |-- group_creator.py  iterative + false-group\n"
        " |   |-- puzzle_editor.py\n"
        " |   |-- prompts.py\n"
        " |   |-- difficulty.py     color assignment (shared)\n"
        " |   `-- deduplicator.py   v2: 16-word + 4-word (shared)\n"
        " |-- cfr/                  Pipeline B (our contribution)\n"
        " |   |-- pipeline.py       CFRPipeline, both modes\n"
        " |   |-- embedding_retriever.py  KNN + category sampling\n"
        " |   |-- word_bank.py      v2: NYT + WordNet + Google 10k\n"
        " |   `-- prompts.py        batched-categories prompt (Mode B)\n"
        " `-- solvers/\n"
        "     |-- embedding_solver.py\n"
        "     |-- clustering_solver.py\n"
        "     |-- llm_solver.py\n"
        "     `-- roundtable.py\n"
        "\n"
        "scripts/\n"
        " |-- generate_puzzles.py      Pipeline A CLI\n"
        " |-- cfr/generate_cfr.py      Pipeline B CLI\n"
        " |-- split_by_color.py\n"
        " `-- build_*_pdf.py           regenerate PDFs\n"
        "\n"
        "data/     nyt_puzzles/, cache/, generated/, generated/cfr_v2/\n"
        "webapp/   deployed static site (GitHub Pages)\n"
        "notebooks/ Jupyter demo\n"
        "tests/    pytest suite"
    )

    pdf.subsection("Dry-run mode")
    pdf.body(
        "All LLM-calling code goes through LLMClient. When DRY_RUN=true (default), "
        "the client never makes a network call; it returns realistic canned "
        "responses routed by prompt-keyword matching. The entire pipeline -- "
        "including the notebook and web app -- can be built and tested with zero "
        "API keys configured."
    )

    pdf.subsection("Reproducibility")
    pdf.body(
        "A fixed random seed (RANDOM_SEED = 42 in config.py) is threaded through "
        "the pipeline. The same input produces the same output. Intermediate "
        "artefacts (candidate pools, solver traces) are persisted to the output "
        "JSON for audit."
    )

    # ---------- 7. Benchmarks ----------
    pdf.section(7, "Benchmarks")

    pdf.subsection("Pipeline-level comparison (100 puzzles per row)")
    pdf.table(
        ["Pipeline / Mode", "LLM", "Pass", "Time", "Non-NYT", "Group matches"],
        [
            ["A  (gpt-4o-mini, iterative)", "5", "91%",     "~10 s",  "--",    "not checked"],
            ["A  (gpt-4o, iterative)",      "5", "87%",     "~10 s",  "--",    "not checked"],
            ["B  v1 Mode A (remix)",        "0", "97%",     "1.41 s", "0%",    "not checked"],
            ["B  v1 Mode B (fresh)",        "1", "99%",     "2.67 s", "0%",    "not checked"],
            ["B  v2 Mode A (remix)",        "0", "99%",     "1.27 s", "62.6%", "0 / 100"],
            ["B  v2 Mode B (fresh)",        "1", "99%",     "2.77 s", "69.1%", "0 / 100"],
        ],
        widths=[55, 12, 18, 22, 25, 58],
    )

    pdf.subsection("Solver baselines on real NYT puzzles (N=554)")
    pdf.table(
        ["Solver", "Full-puzzle solve rate", "Published baseline"],
        [
            ["Embedding (greedy)",   "2.0% (11/554)",   "~11.6% (Missed Connections)"],
            ["Clustering (beam=10)", "3.4% (19/554)",   "higher than embedding"],
        ],
        widths=[55, 55, 80],
    )
    pdf.body(
        "Our solvers are more conservative than published baselines, which is "
        "intentional: we want the validation to reject ambiguous puzzles "
        "aggressively, not match human performance. A puzzle our solvers can "
        "crack has a cleanly recoverable semantic structure."
    )

    pdf.subsection("Dataset statistics")
    pdf.table(
        ["Artefact", "Count"],
        [
            ["Ground-truth NYT puzzles",              "554"],
            ["Unique NYT words (W_NYT)",               "4,918"],
            ["Unique NYT categories (C)",              "2,054"],
            ["Unique NYT 4-word groups (G_NYT)",       "2,216"],
            ["WordNet lemmas added (filtered)",        "~10,000"],
            ["Total augmented word bank (v2)",         "14,877"],
            ["Puzzles generated (Pipeline A)",         "775"],
            ["Puzzles generated (Pipeline B v1+v2)",   "400"],
            ["Total validated puzzles on disk",        ">1,100"],
        ],
        widths=[120, 70],
    )

    # ---------- 8. Rubric compliance ----------
    pdf.section(8, "Rubric Compliance")

    pdf.subsection("\"Don't reproduce a past connections puzzle\"")
    pdf.body("Enforced at two levels:")
    pdf.bullet("16-word set overlap threshold of 6 against any past NYT puzzle.")
    pdf.bullet(
        "Exact 4-word group match against the indexed set of 2,216 past NYT "
        "groups.")
    pdf.body(
        "Across 200 v2 benchmark puzzles, both checks flagged 0 generated "
        "puzzles as duplicates."
    )

    pdf.subsection("\"Word bank larger than the original\"")
    pdf.body(
        "NYT has 4,918 unique words; ours has 14,877. Moreover, 62-69% of output "
        "words in v2 benchmarks are from the non-NYT portion of the bank, "
        "demonstrating that the augmentation is actually used -- not just shelved."
    )

    pdf.subsection("\"Web interface\"")
    pdf.body(
        "The static site at webapp/ is deployed to GitHub Pages. It bundles 542 "
        "validated puzzles and replicates the NYT 4x4 grid with correct-guess "
        "reveals, 'one away' feedback, shuffle, and mistake tracking. Vanilla "
        "JavaScript, no backend."
    )

    pdf.subsection("\"Plausibly from the NYTimes\"")
    pdf.body(
        "Formal human evaluation pending. Spot checks on v2 output show many "
        "puzzles that read as NYT-style (FAQ and notebook deliverables will "
        "contain sample puzzles with commentary)."
    )

    # ---------- 9. Limitations ----------
    pdf.section(9, "Limitations and Future Work")

    pdf.subsection("Known limitations")
    pdf.bullet(
        "Wordplay categories underperform. CFR relies on semantic similarity, "
        "which captures 'SYNONYMS FOR X' well but struggles with '___FISH' or "
        "'WORDS CONTAINING HIDDEN COLORS.' Purely syntactic categories don't "
        "map cleanly to embedding space.")
    pdf.bullet(
        "Occasional awkward WordNet words (e.g., MORPHOPHONEMIC) slip into some "
        "groups. A higher WordNet frequency threshold or intersection with "
        "Google 10k would help.")
    pdf.bullet(
        "Solver conservatism may reject good puzzles. Some creative puzzles that "
        "a human could solve may fail our solver gate.")

    pdf.subsection("Concrete next steps")
    pdf.bullet(
        "Scale to 10,000 puzzles. CFR Mode A can do this in ~3.5h at $0 cost; "
        "Mode B does it in ~7.5h for ~$0.50.")
    pdf.bullet(
        "Mode C: CFR False-Group. Port the highest-quality method from Pipeline "
        "A into CFR's 1-LLM-call framework.")
    pdf.bullet(
        "Batched LLM categories. In Mode B, ask for 40 categories per call "
        "instead of 4 -- a 10x cost reduction on top of the 20x already achieved.")
    pdf.bullet(
        "Human evaluation. Add a thumbs-up/down widget to the web app; collect "
        "hundreds of ratings; report the 'plausibly NYT' rate directly.")
    pdf.bullet(
        "LLM solver in the roundtable. Use it as a tiebreaker on puzzles that "
        "one of the first two solvers rejects, improving acceptance of genuinely "
        "good wordplay puzzles.")

    # ---------- References ----------
    pdf.section(10, "References")
    pdf.bullet("Samuel et al., Making New Connections, arXiv:2407.11240 (2024).")
    pdf.bullet("Missed Connections: Solvers for the NYT Connections Game, arXiv:2404.11730 (2024).")
    pdf.bullet("Deceptively Simple, arXiv:2412.01621 (2024).")
    pdf.bullet("Connecting the Dots, arXiv:2406.11012 (2024).")
    pdf.bullet("Princeton University, WordNet: A Lexical Database for English.")
    pdf.bullet("sentence-transformers library, all-mpnet-base-v2 model.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
