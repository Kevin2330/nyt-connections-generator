"""Build the FAQ PDF via fpdf2."""

import sys
from pathlib import Path
from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "docs" / "final_faq.pdf"


class FAQ(FPDF):
    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(95, 5, "Infinite Connections -- FAQ", align="L")
        self.cell(95, 5, "STA 561D | Duke", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(180, 180, 180)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section(self, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(26, 84, 144)
        self.ln(3)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(26, 84, 144)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_text_color(0, 0, 0)
        self.ln(1)

    def qa(self, question, answer_paragraphs):
        # Q line
        self.ln(1.5)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(26, 84, 144)
        self.set_x(10)
        self.multi_cell(190, 5, f"Q.  {question}")
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 10)
        # A paragraphs
        if isinstance(answer_paragraphs, str):
            answer_paragraphs = [answer_paragraphs]
        for i, para in enumerate(answer_paragraphs):
            self.set_x(10)
            prefix = "A.  " if i == 0 else "    "
            self.multi_cell(190, 4.5, prefix + para)
            self.ln(0.5)

    def bullets(self, items):
        self.set_font("Helvetica", "", 10)
        for item in items:
            self.set_x(14)
            self.multi_cell(186, 4.5, "  -  " + item)
        self.ln(0.5)

    def table(self, headers, rows, widths=None):
        if widths is None:
            widths = [190 / len(headers)] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(220, 230, 245)
        self.set_draw_color(100, 100, 100)
        for w, h in zip(widths, headers):
            self.cell(w, 6, h, border=1, fill=True, align="L")
        self.ln(6)
        self.set_font("Helvetica", "", 9)
        for i, row in enumerate(rows):
            fill = (i % 2 == 0)
            self.set_fill_color(248, 248, 248)
            for w, cell in zip(widths, row):
                self.cell(w, 5.5, str(cell), border=1, fill=fill, align="L")
            self.ln(5.5)
        self.ln(1)


def build():
    pdf = FAQ(orientation="P", unit="mm", format="Letter")
    pdf.set_margins(10, 12, 10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(26, 84, 144)
    pdf.ln(2)
    pdf.cell(0, 8, "Infinite Connections", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 6, "Frequently Asked Questions",
             align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 4,
        "Abuzar  |  Adreama  |  Burak  |  Hengkai  |  Kaiwen",
        align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 4, "STA 561D  |  Duke University  |  April 2026",
        align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    # Intro
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "This FAQ anticipates the questions a careful, skeptical reader would "
        "ask after reading our executive summary or technical appendix. We've "
        "grouped them by topic: the methodology, the safety rules, the division "
        "of work across five teammates, the results, and the limitations.")

    # ================ METHODOLOGY ================
    pdf.section("Methodology")

    pdf.qa("Why did you build five different methods instead of picking the best one?",
        "The Connections puzzle is deceptively hard. A single method tends to be "
        "great at one category style and weak at others: semantic-similarity "
        "approaches nail 'SYNONYMS FOR X' but stumble on wordplay like '___FISH' "
        "or hidden patterns like 'WORDS CONTAINING COLORS.' By dividing the work "
        "across five complementary methods -- AI-heavy iterative (Adreama), "
        "pattern-driven dictionary (Burak), yellow-only specialist (Hengkai), "
        "embedding retrieval (Kaiwen), and multi-agent critic (Abuzar) -- we "
        "cover more of the puzzle design space than any one approach could. It "
        "also matches the professor's suggestion that we 'identify the different "
        "mechanisms in which words are grouped and build separate generators "
        "for each.'")

    pdf.qa("What is the 'Category-First Retrieval' method that keeps getting mentioned?",
        "It is one of our novel contributions (Kaiwen). Traditional methods ask "
        "the AI to produce every word; then a deterministic step picks the best "
        "4 out of 8. That's wasteful -- four of the AI's eight words are always "
        "thrown away. CFR inverts the flow: the AI produces only the CATEGORY "
        "NAME, and a word-lookup against a 14,877-word dictionary finds the 30 "
        "most closely related words, from which we pick the best four. One AI "
        "call replaces five, at the same (or better) quality.")

    pdf.qa("Why use embeddings at all -- aren't LLMs just as good?",
        "LLMs are good at creative naming but inconsistent at ranking. Asked to "
        "pick 'the best 4 of these 8 words,' an LLM gives different answers "
        "each time depending on temperature, seed, and context. Embeddings "
        "(numerical fingerprints of each word's meaning) give us DETERMINISTIC "
        "similarity scores: we get the same answer every time, which makes "
        "difficulty colors and validation reproducible. The combined approach "
        "-- LLM for naming, embeddings for ranking -- gets the best of both "
        "worlds.")

    pdf.qa("How do the teammates' methods fit together?",
        "We publish each method separately so they can be compared, but they "
        "share the same post-processing pipeline:")
    pdf.bullets([
        "Difficulty color assignment via within-group cohesion scores",
        "Deduplication against the 554 past NYT puzzles",
        "Multi-solver roundtable validation (two independent algorithms must agree)",
    ])
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "So every puzzle, regardless of which teammate's generator made it, "
        "passes through the same quality gate.")

    pdf.qa("Why did Hengkai focus only on yellow, and Burak only on non-purple?",
        "The NYT's yellow category is always the easiest and the most "
        "semantically cohesive; a specialist who tunes just for yellow can "
        "produce unusually high-quality easy groups. Purple, the hardest, "
        "depends heavily on wordplay and hidden patterns -- which are hard for "
        "embedding-based methods. Rather than produce mediocre purples, "
        "Hengkai and Burak focused where their technique excels, while the more "
        "general pipelines (Adreama, Kaiwen, Abuzar) handled the full puzzle.")

    # ================ SAFETY ================
    pdf.section("Safety and duplication")

    pdf.qa("How do you know you aren't just reproducing past NYT puzzles?",
        "We built two independent checks:")
    pdf.bullets([
        "16-word overlap: flag any candidate whose 16 words share more than 6 "
        "with any of the 554 past NYT puzzles.",
        "4-word group match: flag any candidate whose 4-word group exactly "
        "matches any of the 2,216 past NYT 4-word groups.",
    ])
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "Our pipeline doesn't just detect these collisions post-hoc -- during "
        "word selection, it also skips any 4-word combination that matches a "
        "past NYT group and picks the next-best one instead. Across 500+ "
        "benchmark puzzles, zero have triggered either check. The hard-fail "
        "rule cannot be violated without removing the guard.")

    pdf.qa("Could the LLM leak a memorized NYT puzzle?",
        "The underlying language models were trained on web text, so they have "
        "seen Connections discussions. But our pipeline never lets the LLM "
        "output the final word list directly; the LLM only proposes categories "
        "or pools, and the word choice is done by deterministic dictionary "
        "lookup. Even if the LLM suggested a real NYT group, the group-level "
        "dedup check catches it before acceptance.")

    pdf.qa("What about near-duplicates -- a puzzle with 5 overlapping words?",
        "Our threshold is 6 (any overlap of 7 or more words flags the puzzle). "
        "With 16-word puzzles drawn from a 14,877-word bank, overlapping 5 or 6 "
        "words happens by chance maybe once in thousands of puzzles. We report "
        "the overlap counts in every puzzle's metadata so a reviewer can audit "
        "this directly.")

    # ================ QUALITY ================
    pdf.section("Quality and evaluation")

    pdf.qa("99% pass rate -- doesn't that mean your solver is too lenient?",
        "We don't trust our own solvers to be lenient; that's why we run TWO "
        "independent ones. A puzzle is accepted only if at least one solver "
        "fully recovers the intended 4-group partition. Both solvers use "
        "deterministic algorithms (greedy cosine selection and beam-search "
        "clustering) and solve only 2-3% of the real NYT puzzles -- they are "
        "conservative, not easy. So a puzzle that our solvers CAN crack has a "
        "cleanly recoverable structure (exactly what a good puzzle should have).")

    pdf.qa("How close to the NYT style are the puzzles, really?",
        "The rubric's A+ target is that TAs rate at least 40% of our puzzles "
        "as 'plausibly having come from the NYTimes.' We haven't yet run a "
        "formal human evaluation; we added a thumbs-up/thumbs-down button to "
        "the web app so ratings can be collected at scale. Internally, on the "
        "categories where our system excels (synonyms, types-of-X, themed "
        "nouns) many puzzles are indistinguishable from NYT to a casual reader. "
        "On pure wordplay categories ('___FISH,' letter homophones), the output "
        "is weaker -- that is a real limitation we describe below.")

    pdf.qa("What's the unique-solution guarantee?",
        "A Connections puzzle is only valid if exactly one 4-way partition "
        "fits the intended themes. We enforce this in two ways: (1) during "
        "generation, CFR's candidate selector skips any 4-word group with a "
        "high cross-group 'bleed' score (words that fit another group too "
        "well), and (2) during validation, our two solvers must find the "
        "intended partition -- if they find a DIFFERENT partition that also "
        "satisfies the themes, the puzzle is rejected as ambiguous.")

    pdf.qa("Is the word bank big enough?",
        "The NYT has used about 4,918 unique words across all 554 of its "
        "puzzles. Our augmented bank has 14,877 WORDS -- three times larger. "
        "In the output, 62-69% of generated words come from the NON-NYT "
        "portion, showing that the expansion is actually being used, not just "
        "sitting on disk.")

    # ================ COST & SCALE ================
    pdf.section("Cost and scale")

    pdf.qa("What does it cost to generate the 10,000 puzzles the rubric mentions?",
        "Here is the cost breakdown per method at 10,000-puzzle scale:")
    pdf.table(
        ["Method", "Cost / 10,000 puzzles"],
        [
            ["Kaiwen CFR Mode A (no AI calls)",        "$0"],
            ["Kaiwen CFR Mode B (1 AI call each)",     "~$3"],
            ["Burak pattern-builder (no AI calls)",    "$0"],
            ["Hengkai yellow specialist",              "~$1"],
            ["Adreama iterative (4 AI calls each)",    "~$40"],
            ["Pipeline A baseline (5 AI calls each)",  "~$50"],
        ],
        widths=[130, 60],
    )
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "Even the most expensive method is within a routine student budget. "
        "The cheap methods let us generate unlimited puzzles at zero cost.")

    pdf.qa("Why are different methods cheaper than others?",
        "Because they make fewer calls to the paid AI service. Adreama asks "
        "the AI four times per puzzle. Pipeline A asks five times. Kaiwen's "
        "CFR Mode B asks only once. Kaiwen's CFR Mode A and Burak's method "
        "don't ask the AI at all -- they use only dictionaries and math, "
        "which are free to run on a laptop.")

    pdf.qa("Will this scale to 100,000 puzzles?",
        "Yes. CFR Mode A runs at about 1.3 seconds per puzzle on a single "
        "laptop CPU with no network calls, so 100,000 puzzles take about 36 "
        "hours of wall time and cost $0. The bottleneck at that scale would "
        "be the roundtable validator, not generation.")

    # ================ REPRODUCIBILITY ================
    pdf.section("Reproducibility")

    pdf.qa("Can someone else reproduce your results without API keys?",
        "Yes. The code ships with a DRY_RUN=true default: every call to the "
        "AI service is intercepted and replaced by a realistic mock response. "
        "The master notebook, the web app, the test suite, and the solver "
        "benchmark all run end-to-end with no keys configured. Turning "
        "DRY_RUN=false (and setting OPENAI_API_KEY) switches to real calls.")

    pdf.qa("How do I re-run the benchmarks?",
        "Two commands:")
    pdf.set_font("Courier", "", 9)
    pdf.set_x(14)
    pdf.multi_cell(186, 5,
        "python scripts/cfr/generate_cfr.py --mode remix --count 100\n"
        "python scripts/cfr/generate_cfr.py --mode fresh --count 100")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "Output is written to data/generated/cfr/... with per-puzzle metadata "
        "(pass rate, solver traces, dedup results) for audit.")

    pdf.qa("Where is the code?",
        "Our main repository is at https://github.com/Kevin2330/nyt-connections-generator. "
        "Each teammate's method is in a separate subfolder; the shared pipeline "
        "lives in src/. The live web app "
        "(kevin2330.github.io/nyt-connections-generator/) loads 540+ validated "
        "puzzles from the same repo.")

    # ================ LIMITATIONS ================
    pdf.section("Limitations and future work")

    pdf.qa("What's the biggest weakness of your system?",
        "Wordplay and syntactic categories. Our methods rely on semantic "
        "similarity (how related two words are in meaning), which captures "
        "'SYNONYMS FOR SMART' but not 'WORDS THAT END IN -ING' or '___FISH.' "
        "These pattern-based categories require a different kind of reasoning "
        "-- matching strings and letters -- that embeddings don't naturally "
        "do well. Abuzar's multi-agent system partially addresses this via an "
        "explicit 'concept inspiration' layer, but purple (hardest) categories "
        "remain our weakest output.")

    pdf.qa("Why does WordNet sometimes return awkward words (e.g., MORPHOPHONEMIC)?",
        "WordNet includes many archaic and technical words. We filter by "
        "corpus-frequency and character length, but some oddities slip through. "
        "A higher frequency threshold or intersection with a common-English "
        "list (like the Google 10,000-most-common-words list we optionally "
        "include) would further tighten this.")

    pdf.qa("What would you do next if you had another month?",
        "Three priorities, in order:")
    pdf.bullets([
        "Human evaluation: collect 500+ TA/player ratings via the web app to "
        "measure actual 'plausibly-NYT' percentage.",
        "False-group CFR: port the paper's best single-method technique into "
        "CFR's 1-AI-call framework, which should dramatically improve "
        "hardest-category quality.",
        "Fine-tune embeddings on Connections data: train a specialized "
        "version of the embedding model on the 2,216 past NYT (category, "
        "words) pairs, which would give us much better retrieval for the "
        "wordplay categories we currently handle poorly.",
    ])

    # ================ TEAMWORK ================
    pdf.section("Teamwork")

    pdf.qa("Who did what?", "")
    pdf.table(
        ["Teammate", "Contribution"],
        [
            ["Adreama", "Iterative AI generation with cross-session memory"],
            ["Burak",   "Pattern-driven dictionary builder (green + blue)"],
            ["Hengkai", "Quality-first yellow-difficulty specialist"],
            ["Kaiwen",  "Baseline pipeline + Category-First Retrieval + web app"],
            ["Abuzar",  "Multi-agent critic system + Flask web server"],
        ],
        widths=[35, 155],
    )

    pdf.qa("Did you share code across teammates?",
        "The assignment asks us not to share code, so each teammate's "
        "generator is their own. We share data (the same NYT ground-truth "
        "dataset) and the validation pipeline (Kaiwen's roundtable solvers) "
        "for consistent grading. This means we can directly compare methods on "
        "the same footing without anyone 'winning' by tuning the evaluator.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
