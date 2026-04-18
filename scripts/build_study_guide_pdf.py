"""Build the study guide PDF directly using fpdf2 (no LaTeX compiler needed)."""

import sys
from pathlib import Path
from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "docs" / "study_guide.pdf"


class StudyGuide(FPDF):
    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "Infinite Connections -- Study Guide", align="L")
        self.cell(0, 5, "STA 561D", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section(self, num, title):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 0, 0)
        self.ln(4)
        self.cell(0, 10, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def subsection(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(30, 30, 30)
        self.ln(2)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def subsubsection(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(50, 50, 50)
        self.ln(1)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(10)
        self.multi_cell(190, 5, text)
        self.ln(1)

    def bullet(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(10)
        self.multi_cell(190, 5, "  -  " + text)

    def formula_box(self, title, text):
        self.ln(2)
        self.set_fill_color(255, 248, 220)
        self.set_draw_color(200, 150, 50)
        self.set_font("Helvetica", "B", 9)
        x, y = self.get_x(), self.get_y()
        self.rect(10, y, 190, 8, style="FD")
        self.set_xy(12, y)
        self.cell(0, 8, title)
        self.ln(8)
        self.set_font("Courier", "", 9)
        self.set_fill_color(255, 252, 240)
        lines = text.strip().split("\n")
        block_h = len(lines) * 5 + 4
        y2 = self.get_y()
        self.rect(10, y2, 190, block_h, style="FD")
        self.set_xy(14, y2 + 2)
        for line in lines:
            self.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(14)
        self.ln(3)
        self.set_draw_color(0, 0, 0)

    def key_idea(self, text):
        self.ln(2)
        self.set_fill_color(232, 240, 254)
        self.set_draw_color(60, 100, 180)
        self.set_font("Helvetica", "B", 9)
        y = self.get_y()
        self.rect(10, y, 190, 7, style="FD")
        self.set_xy(12, y)
        self.cell(0, 7, "Key Idea")
        self.ln(7)
        self.set_font("Helvetica", "", 9)
        self.set_fill_color(240, 245, 255)
        y2 = self.get_y()
        # Estimate height
        test_pdf = FPDF()
        test_pdf.add_page()
        test_pdf.set_font("Helvetica", "", 9)
        h_before = test_pdf.get_y()
        test_pdf.multi_cell(186, 5, text)
        h_after = test_pdf.get_y()
        block_h = h_after - h_before + 6
        self.rect(10, y2, 190, block_h, style="FD")
        self.set_xy(13, y2 + 3)
        self.multi_cell(184, 5, text)
        self.ln(3)
        self.set_draw_color(0, 0, 0)

    def table(self, headers, rows, col_widths=None):
        self.ln(2)
        if col_widths is None:
            w = 190 / len(headers)
            col_widths = [w] * len(headers)
        # Header
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(230, 230, 230)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()
        # Rows
        self.set_font("Helvetica", "", 9)
        self.set_fill_color(255, 255, 255)
        for row in rows:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6, str(cell), border=1, align="C")
            self.ln()
        self.ln(2)

    def color_row(self, color_name, hex_color, text):
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        self.set_fill_color(r, g, b)
        self.cell(20, 6, color_name, border=1, fill=True, align="C")
        self.set_fill_color(255, 255, 255)
        self.set_font("Helvetica", "", 9)
        self.cell(170, 6, text, border=1, new_x="LMARGIN", new_y="NEXT")


def build():
    pdf = StudyGuide()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ── Title page ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 15, "Infinite Connections", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.cell(0, 10, "Comprehensive Study Guide", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "AI-Generated NYT Connections Puzzles", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, "STA 561D -- Duke University", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Spring 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(30)

    # ── Table of contents ────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    toc = [
        "1. The Connections Puzzle",
        "2. Foundation: Sentence Embeddings and Cosine Similarity",
        "3. Puzzle Generation Pipeline",
        "4. Solver Algorithms",
        "5. Roundtable Validation",
        "6. Evaluation Metrics",
        "7. System Architecture",
        "8. Key Formulas Reference Card",
        "9. What Is Original vs. From the Literature",
        "10. References",
    ]
    for item in toc:
        pdf.cell(0, 6, item, new_x="LMARGIN", new_y="NEXT")

    # ── Section 1 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("1", "The Connections Puzzle")

    pdf.subsection("What Is It?")
    pdf.body(
        "NYT Connections is a daily word puzzle published by The New York Times. "
        "The player is given 16 words and must sort them into 4 groups of 4, where "
        "each group shares a hidden connection. Groups are color-coded by difficulty:"
    )
    pdf.set_font("Helvetica", "B", 9)
    pdf.color_row("Yellow", "#F9DF6D", "  Easiest -- e.g., WAYS TO SAY HELLO: Hi, Hey, Howdy, Yo")
    pdf.color_row("Green", "#A0C35A", "  Medium -- e.g., PLANETS: Mars, Venus, Saturn, Jupiter")
    pdf.color_row("Blue", "#B0C4EF", "  Hard -- e.g., FIRE ___: Work, Fly, Place, Side")
    pdf.color_row("Purple", "#BA81C5", "  Hardest -- e.g., TAYLOR SWIFT ALBUMS: Folklore, Reputation, ...")
    pdf.ln(3)
    pdf.body("Players get 4 mistakes before losing. A guess of 3/4 correct triggers 'One away!' feedback.")

    pdf.subsection("Why Is Generation Hard?")
    pdf.bullet("Unique solution: 2,627,625 possible groupings, exactly one must be correct.")
    pdf.bullet("Difficulty gradient: groups must range from obvious to subtle.")
    pdf.bullet("Deception: good puzzles contain plausible-but-wrong 'false groups.'")
    pdf.bullet("Diversity: categories span synonyms, wordplay, fill-in-the-blank, pop culture, etc.")

    pdf.subsection("The NYT Dataset")
    pdf.body("We work with a ground truth dataset of 554 NYT Connections puzzles (June 2023 - December 2024).")
    pdf.table(
        ["Metric", "Value"],
        [
            ["Total puzzles", "554"],
            ["Unique words", "4,918"],
            ["Unique categories", "2,054"],
            ["Multi-word entries", "112"],
            ["Puzzles with difficulty", "227 / 554"],
            ["Difficulty mean +/- std", "2.94 +/- 0.64"],
            ["Most frequent word", "BALL (15 appearances)"],
        ],
        [95, 95],
    )
    pdf.body(
        "Category type distribution across 2,216 slots: "
        "Common property 46%, Synonyms/Slang 38%, Fill-in-the-blank 9%, "
        "Pop culture 6%, Wordplay 1%."
    )

    # ── Section 2 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("2", "Foundation: Sentence Embeddings and Cosine Similarity")

    pdf.body(
        "Every component in this project relies on sentence embeddings -- dense vector "
        "representations of words that capture semantic meaning."
    )

    pdf.subsection("The MPNET Model")
    pdf.body(
        "We use all-mpnet-base-v2 from sentence-transformers. It maps each word to a "
        "768-dimensional vector. Words with similar meanings have vectors pointing in "
        "similar directions: 'PIANO' and 'GUITAR' are close; 'PIANO' and 'TRUCK' are far apart."
    )

    pdf.subsection("Cosine Similarity")
    pdf.formula_box("Cosine Similarity", "cos(a, b) = (a . b) / (||a|| * ||b||)\n\nRange: [-1, 1], where 1 = identical direction, 0 = orthogonal")

    pdf.subsection("Average Pairwise Similarity")
    pdf.body("For a group of 4 words, there are C(4,2) = 6 pairs:")
    pdf.formula_box("Average Pairwise Similarity",
                    "s_avg = (1/6) * SUM over all i<j of cos(e_i, e_j)")
    pdf.body("Higher s_avg = words are more semantically related = easier group.")

    pdf.key_idea(
        "Average pairwise cosine similarity is the fundamental building block. It is used for: "
        "(1) selecting the best 4 words from 8 candidates, "
        "(2) scoring groups in the embedding solver, "
        "(3) assigning difficulty colors, and "
        "(4) evaluating puzzle quality."
    )

    # ── Section 3 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("3", "Puzzle Generation Pipeline")
    pdf.body(
        "The pipeline creates puzzles through six stages. The LLM provides creativity; "
        "MPNET provides consistency."
    )

    pdf.subsection("Stage 1: Group Creation (LLM + Embedding Selection)")
    pdf.body(
        "Each puzzle is built one group at a time across 4 LLM calls:\n\n"
        "1. Sample 4 random seed words from the NYT word bank\n"
        "2. LLM generates a category name + 8 candidate words (story-injected)\n"
        "3. MPNET evaluates all C(8,4) = 70 subsets and picks the best 4\n"
        "4. Remove any words already used in previous groups\n"
        "5. Repeat for all 4 groups"
    )

    pdf.key_idea(
        "The LLM is NOT allowed to pick the final 4 words. LLMs are bad at estimating "
        "semantic similarity and make inconsistent selections. MPNET selection is "
        "deterministic and correlates with human difficulty perception."
    )

    pdf.subsubsection("Story Injection for Diversity")
    pdf.body(
        "Without intervention, the LLM generates the same ~20 categories repeatedly. "
        "The story injection technique solves this:\n\n"
        "Prompt: 'First, write a short story (2-3 sentences) using these words: "
        "[4 random words]. Then use that story as inspiration for your category.'\n\n"
        "The random seed words force the LLM into different creative directions each time."
    )

    pdf.subsection("Stage 2: False-Group Method (Primary)")
    pdf.body(
        "This produces the highest-quality puzzles. A user study found that false-group "
        "puzzles beat NYT originals in user preference 42.86% of the time.\n\n"
        "Algorithm:\n"
        "1. LLM generates a 'root group' of 4 words, each with an alternate meaning\n"
        "2. For each root word, generate a NEW category inspired by the alternate meaning\n"
        "3. MPNET selects best 4 from 8 candidates for each new category\n"
        "4. The 4 new categories = the real puzzle; the root group = discarded decoy\n\n"
        "Example: Root = 'THINGS THAT ARE ROUND' -> {BALL, GLOBE, RING, WHEEL}\n"
        "  BALL -> 'formal dance event' -> generates DANCE category\n"
        "  GLOBE -> 'theater or news org' -> generates THEATER category\n"
        "  RING -> 'sound a phone makes' -> generates SOUNDS category\n"
        "  WHEEL -> 'to turn or rotate' -> generates MOVEMENT category\n\n"
        "The solver sees words that LOOK like 'ROUND THINGS', but that group doesn't exist."
    )

    pdf.subsection("Stage 3: Editor Pass")
    pdf.body("A second LLM call reviews the puzzle and fixes inaccurate category names.")

    pdf.subsection("Stage 4: Difficulty Color Assignment")
    pdf.formula_box("Color Assignment Rule",
                    "1. Compute avg pairwise cosine similarity for each group\n"
                    "2. Sort groups by similarity DESCENDING\n"
                    "3. Assign: highest -> Yellow, next -> Green, next -> Blue, lowest -> Purple")
    pdf.body("Intuition: high similarity = words obviously relate = easy. Low similarity = subtle connection = hard.")

    pdf.body("Empirical thresholds (paper vs. our measurements on 554 NYT puzzles):")
    pdf.table(
        ["Color", "Paper Mean", "Our Mean", "Our Std"],
        [
            ["Yellow", "0.40", "0.389", "0.089"],
            ["Green", "0.35", "0.315", "0.060"],
            ["Blue", "0.29", "0.268", "0.050"],
            ["Purple", "0.27", "0.225", "0.049"],
        ],
        [47, 47, 48, 48],
    )
    pdf.body(
        "NYT color matches similarity rank only 43.9% of the time, confirming that "
        "difficulty has a knowledge/wordplay component embeddings cannot capture."
    )

    pdf.subsection("Stage 5: Deduplication")
    pdf.body(
        "Each puzzle's 16-word set is compared against all 554 NYT puzzles. "
        "If more than 6 words overlap with any single NYT puzzle, it is flagged."
    )

    pdf.subsection("Pipeline Summary")
    pdf.table(
        ["Stage", "Who", "Why"],
        [
            ["Group creation", "LLM", "Invents categories + candidates"],
            ["Word selection", "MPNET", "Picks most cohesive 4 from 8"],
            ["Editor pass", "LLM", "Fixes inaccurate names"],
            ["Color assignment", "MPNET", "Maps similarity to difficulty"],
            ["Deduplication", "Set math", "Prevents copying NYT puzzles"],
        ],
        [45, 30, 115],
    )

    # ── Section 4 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("4", "Solver Algorithms")
    pdf.body("Three independent solvers verify that each puzzle has exactly one valid solution.")

    pdf.subsection("Solver 1: Embedding Solver (Greedy)")
    pdf.body(
        "Source: 'Missed Connections' paper (arXiv:2404.11730).\n\n"
        "Algorithm:\n"
        "1. Encode all 16 words with MPNET\n"
        "2. Compute 16x16 cosine similarity matrix\n"
        "3. Score all C(16,4) = 1,820 possible groups by avg pairwise similarity\n"
        "4. Sort by score descending\n"
        "5. Greedily pick the highest-scoring non-overlapping groups (4 total)\n\n"
        "Complexity: O(1,820) group evaluations + sorting.\n"
        "Runtime: ~0.019s per puzzle.\n"
        "Accuracy: 2.0% full-puzzle solve rate.\n\n"
        "Limitation: greedy selection can 'use up' key words in a wrong group, "
        "causing cascading errors. The solver never backtracks."
    )

    pdf.subsection("Solver 2: Clustering Solver (Beam Search)")
    pdf.body("Source: 'Deceptively Simple' paper (arXiv:2412.01621).")

    pdf.subsubsection("Group Similarity Score (G)")
    pdf.formula_box(
        "Group Similarity Score",
        "G = 0.4 * I + 0.3 * s + 0.3 * V\n"
        "\n"
        "I = -SUM( ||e_i - centroid||^2 )    (negative k-means inertia)\n"
        "s = MIN over all i<j of cos(e_i, e_j)  (weakest link)\n"
        "V = mean(P) / (1 + var(P))           (stability-weighted mean)\n"
        "\n"
        "P = {cos(e_i, e_j) : i < j}   (all 6 pairwise similarities)",
    )
    pdf.body(
        "Intuition for each component:\n"
        "- I (inertia): How tightly clustered? Tighter = higher score.\n"
        "- s (min similarity): A group is only as strong as its weakest pair.\n"
        "- V (stability): Rewards consistent similarity. A group with all pairs at 0.3 "
        "scores higher than {0.5, 0.5, 0.5, 0.1, 0.1, 0.1} even if means are equal."
    )

    pdf.subsubsection("Penalty Score (P)")
    pdf.formula_box(
        "Penalty Score",
        "P = (1/|R|) * SUM over r in R of cos(centroid_C, r)\n"
        "\n"
        "R = remaining words after removing group C\n"
        "centroid_C = mean of group C's embeddings\n"
        "\n"
        "Lower penalty = better separation from remaining words",
    )

    pdf.subsubsection("Beam Search")
    pdf.body(
        "Algorithm:\n"
        "1. Initialize beam with empty grouping (all 16 words remaining)\n"
        "2. For each of 4 steps:\n"
        "   a. For each state in the beam, enumerate all C(remaining, 4) groups\n"
        "   b. Score each: cumulative += G - P\n"
        "   c. Keep top 10 candidates (beam width)\n"
        "3. Return the highest-scoring complete 4-group solution\n\n"
        "Step sizes: Step 1: 10 x 1,820 = 18,200 evaluations.\n"
        "Step 2: 10 x 495. Step 3: 10 x 70. Step 4: 10 x 1.\n\n"
        "Runtime: ~0.95s per puzzle (~50x slower than embedding solver).\n"
        "Accuracy: 3.4% full-puzzle solve rate."
    )

    pdf.subsection("Solver 3: LLM Solver (Chain-of-Thought)")
    pdf.body(
        "Source: 'Missed Connections' paper. Presents all 16 words to Claude with "
        "step-by-step reasoning instructions. Most human-like but expensive (API call "
        "per puzzle). Used as a tiebreaker only."
    )

    pdf.subsection("Solver Performance Comparison")
    pdf.table(
        ["Metric", "Embedding", "Clustering"],
        [
            ["Full solve rate", "2.0% (11/554)", "3.4% (19/554)"],
            ["Avg groups correct", "0.57 / 4", "0.71 / 4"],
            ["Yellow accuracy", "24.5%", "28.0%"],
            ["Green accuracy", "17.7%", "22.6%"],
            ["Blue accuracy", "9.8%", "13.0%"],
            ["Purple accuracy", "5.1%", "7.6%"],
            ["Runtime (554 puzzles)", "10.6s", "525s"],
        ],
        [60, 65, 65],
    )
    pdf.body(
        "Both solvers show the expected difficulty gradient. The clustering solver "
        "outperforms across all colors at ~50x the compute cost. They agreed on a "
        "full solve for only 7 puzzles (1.3%), confirming complementary approaches."
    )

    # ── Section 5 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("5", "Roundtable Validation")
    pdf.key_idea(
        "This is the project's most original contribution. The papers each address "
        "generation OR solving; we combine them by using solver agreement as a quality "
        "gate for generated puzzles."
    )

    pdf.subsection("The Core Idea")
    pdf.body(
        "A valid Connections puzzle must have exactly one correct solution. If two "
        "independent solvers, using completely different algorithms, both find the same "
        "grouping -- and that matches the intended answer -- then the puzzle is unambiguous.\n\n"
        "If they disagree, the puzzle has competing interpretations and should be discarded."
    )

    pdf.subsection("Validation Logic")
    pdf.body(
        "1. Run Embedding Solver on the 16 words -> solution S1\n"
        "2. Run Clustering Solver on the 16 words -> solution S2\n"
        "3. Normalize both to sets of frozensets (order-independent)\n"
        "4. Check: S1 == S2? (same 4 groups?)\n"
        "5. Check: do they match the intended answer?\n"
        "6. Valid = agreement AND at least one solver got all 4 correct"
    )

    pdf.subsection("Why Two Solvers?")
    pdf.body(
        "The embedding solver (greedy, optimizes avg pairwise similarity) and "
        "clustering solver (beam search, optimizes G - P composite) have different "
        "failure modes. When both converge to the same answer, it is strong evidence "
        "that the answer is unique."
    )

    # ── Section 6 ────────────────────────────────────────────────────────
    pdf.section("6", "Evaluation Metrics")
    pdf.body(
        "Group Similarity Score (G): identical to the clustering solver's formula. "
        "Used as an independent quality metric.\n\n"
        "Penalty Score (P): measures group-group separation.\n\n"
        "Puzzle-level quality:\n"
        "- Overall avg similarity: mean of s_avg across all 4 groups\n"
        "- Similarity spread: max(s_avg) - min(s_avg). Should be positive.\n"
        "- Solver agreement rate: fraction of puzzles where solvers converge\n"
        "- Category diversity: number of unique category names"
    )

    # ── Section 7 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("7", "System Architecture")

    pdf.subsection("Data Flow")
    pdf.body(
        "LLM (8 candidates) -> MPNET (select best 4) -> Editor (LLM) -> Difficulty (MPNET)\n"
        "         |                                                            |\n"
        "         v                                                            v\n"
        "   Deduplication                                              Roundtable Validator\n"
        "                                                              Agree? -> Accept / Discard"
    )

    pdf.subsection("Dry-Run Mode")
    pdf.body(
        "All LLM calls go through LLMClient, which checks dry_run. If true, "
        "MockLLMClient returns realistic hardcoded responses by detecting request "
        "type from prompt keywords. MPNET always runs for real."
    )
    pdf.table(
        ["Component", "Dry-run", "Real mode"],
        [
            ["Category ideas + pools", "Mock", "Claude API"],
            ["Word selection (8->4)", "Real MPNET", "Real MPNET"],
            ["Editor pass", "Mock", "Claude API"],
            ["Difficulty colors", "Real MPNET", "Real MPNET"],
            ["Embedding solver", "Real MPNET", "Real MPNET"],
            ["Clustering solver", "Real MPNET", "Real MPNET"],
            ["LLM solver", "Mock", "Claude API"],
        ],
        [70, 60, 60],
    )

    # ── Section 8 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section("8", "Key Formulas Reference Card")
    pdf.formula_box(
        "All Formulas in One Place",
        "COSINE SIMILARITY:\n"
        "  cos(a, b) = (a . b) / (||a|| * ||b||)\n"
        "\n"
        "AVERAGE PAIRWISE SIMILARITY (4 words):\n"
        "  s_avg = (1/6) * SUM_i<j cos(e_i, e_j)\n"
        "\n"
        "GROUP SIMILARITY SCORE:\n"
        "  G = 0.4 * I  +  0.3 * s  +  0.3 * V\n"
        "  I = -(SUM ||e_i - centroid||^2)       [neg. inertia]\n"
        "  s = MIN_i<j cos(e_i, e_j)             [weakest link]\n"
        "  V = mean(P) / (1 + var(P))            [stability]\n"
        "\n"
        "PENALTY SCORE:\n"
        "  P = (1/|R|) * SUM_r cos(centroid_C, r)\n"
        "\n"
        "BEAM SEARCH OBJECTIVE:\n"
        "  maximize SUM_groups (G - P)\n"
        "\n"
        "COLOR ASSIGNMENT:\n"
        "  sort by s_avg descending -> Yellow, Green, Blue, Purple\n"
        "\n"
        "VALIDATION:\n"
        "  valid = (solver1 == solver2) AND (any solver got 4/4)",
    )

    # ── Section 9 ────────────────────────────────────────────────────────
    pdf.section("9", "What Is Original vs. From the Literature")
    pdf.table(
        ["Component", "Status", "Source"],
        [
            ["Embedding solver", "Reimplementation", "Missed Connections (2404.11730)"],
            ["Clustering solver", "Reimplementation", "Deceptively Simple (2412.01621)"],
            ["False-group pipeline", "Reimplementation", "Making New Connections (2407.11240)"],
            ["Color thresholds", "Constants", "Making New Connections Table 1"],
            ["LLM solver (CoT)", "Reimplementation", "Missed Connections"],
            ["Roundtable validator", "NOVEL", "Original to this project"],
            ["Prompt templates", "NOVEL", "Original text"],
            ["Mock/dry-run system", "NOVEL", "Original engineering"],
            ["Web app", "NOVEL", "Original code"],
            ["End-to-end integration", "NOVEL", "Papers do gen OR solving; we combine"],
        ],
        [50, 40, 100],
    )
    pdf.body("All code is written from scratch. No code was copied from any reference repository.")

    # ── Section 10 ───────────────────────────────────────────────────────
    pdf.section("10", "References")
    pdf.body(
        "[1] Conneau et al., 'Making New Connections,' arXiv:2407.11240, 2024.\n"
        "    Generation pipeline, false groups, story injection, color thresholds.\n\n"
        "[2] Todd et al., 'Missed Connections,' arXiv:2404.11730, 2024.\n"
        "    Embedding solver, LLM solver baselines, CoT prompts.\n\n"
        "[3] Li et al., 'Deceptively Simple,' arXiv:2412.01621, 2024.\n"
        "    G = 0.4I + 0.3s + 0.3V formula, penalty score, beam search.\n\n"
        "[4] Patel et al., 'Connecting the Dots,' arXiv:2406.11012, 2024.\n"
        "    Category types, human evaluation methodology."
    )

    pdf.output(str(OUT))
    print(f"PDF saved to {OUT}")
    print(f"Pages: {pdf.pages_count}")


if __name__ == "__main__":
    build()
