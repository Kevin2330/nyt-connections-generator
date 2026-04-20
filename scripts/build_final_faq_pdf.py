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
        self.ln(1.5)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(26, 84, 144)
        self.set_x(10)
        self.multi_cell(190, 5, f"Q.  {question}")
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "", 10)
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

    # Title block
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
        "ask after reading our executive summary or technical report. We group "
        "them by topic: how each of the five teammates' methods works, how we "
        "prevent duplicates, how we measure quality, cost and scale, and known "
        "limitations.")

    # ================ INDIVIDUAL METHODS ================
    pdf.section("The five methods, explained individually")

    pdf.qa("What method did Kaiwen build?",
        "Kaiwen implemented two pipelines head-to-head. Pipeline A is a "
        "reference implementation of the iterative generator from the 'Making "
        "New Connections' paper -- five AI calls per puzzle, one for each of "
        "the four groups plus a final editor pass. Pipeline B is a new design "
        "called CATEGORY-FIRST RETRIEVAL (CFR): instead of asking the AI to "
        "produce words, it asks the AI only for CATEGORY NAMES, and then a "
        "word-lookup against a 14,877-word dictionary finds the best matching "
        "words. Mode A of CFR uses zero AI calls (it samples category names "
        "from the existing NYT catalog); Mode B uses one AI call per puzzle to "
        "invent fresh category names. One AI call replaces five at the same "
        "quality.")

    pdf.qa("What method did Adreama build?",
        "Adreama's method is a single-call iterative generator. A GPT-4.1 call "
        "returns all four groups at once as structured JSON, with a long "
        "context prompt that carries forward every word and category the "
        "generator has used across sessions. The generator keeps three "
        "persistent memory files (used_words.json, used_categories.json, "
        "used_boards.json) so duplicates never creep in even over thousands of "
        "puzzles. A library of 48 hand-curated 'category webs' (tuples of REAL "
        "+ TRAP categories) seeds thematic false-group designs. The generator "
        "retries up to four times on parse or validation errors; batches of "
        "50 attempts typically yield ~35 valid puzzles.")

    pdf.qa("What method did Burak build?",
        "Burak's method is almost entirely non-AI -- the AI only gets called "
        "to label one group. The pipeline builds puzzles color by color, each "
        "color using a different algorithm: PURPLE is drawn from a pool scored "
        "by eight rule-based mechanisms (e.g., collective nouns, contronyms), "
        "optionally with a machine-learning classifier reranking the pool; "
        "GREEN is built by rhyme anchors using the CMU pronunciation dictionary; "
        "BLUE is a niche-category generator where Claude Haiku validates the "
        "group; and YELLOW uses word2vec semantic clusters. 'Impostor' words "
        "are planted deliberately to create false-group pressure across colors.")

    pdf.qa("What method did Hengkai build?",
        "Hengkai is the yellow-difficulty specialist. The generator is fully "
        "algorithmic -- zero AI calls -- and uses pre-computed GloVe word "
        "embeddings, ConceptNet relations, and corpus frequency filters. "
        "Candidates are scored within several relation types (taxonomic, "
        "synonymy, verb-noun association, ConceptNet link) and the "
        "highest-scoring combinations become yellow groups. It is the only "
        "teammate's generator that validates each candidate group against the "
        "full 554-puzzle NYT history before acceptance, rejecting any group "
        "that shares three or more words with a past NYT group. A checkpoint "
        "system lets batch runs of 700+ puzzles resume after interruption.")

    pdf.qa("What method did Abuzar build?",
        "Abuzar's method is an agent-oriented system. A single GPT-4.1 call "
        "produces the full 4-group puzzle in JSON, but the prompt is heavily "
        "engineered with banned-category lists, banned-purple-type counters, "
        "and a trap-word mechanism where one purple word is specifically "
        "designed to impersonate a simpler category. The pipeline enforces "
        "self-uniqueness through persistent word, category, and board-signature "
        "sets; it also ships with a Flask web server and a 'concept inspirations' "
        "library for theme variety. It does NOT check against the 554 past "
        "NYT puzzles -- only against its own generated history.")

    pdf.qa("Why build five different methods instead of picking the best one?",
        "The Connections puzzle is deceptively hard. A single method tends to "
        "be great at one category style and weak at others: semantic-similarity "
        "approaches nail 'SYNONYMS FOR X' but stumble on wordplay like '___FISH' "
        "or hidden patterns like 'WORDS CONTAINING COLORS.' By spreading the "
        "work across five complementary methods we cover more of the design "
        "space than any one approach could. It also matches the professor's "
        "suggestion that we IDENTIFY THE DIFFERENT MECHANISMS IN WHICH WORDS "
        "ARE GROUPED AND BUILD SEPARATE GENERATORS FOR EACH.")

    pdf.qa("Why use embeddings at all -- aren't LLMs just as good?",
        "LLMs are good at creative naming but inconsistent at ranking. Asked "
        "to pick 'the best 4 of these 8 words,' an LLM gives different answers "
        "each time depending on temperature, seed, and context. Embeddings "
        "(numerical fingerprints of each word's meaning) give us DETERMINISTIC "
        "similarity scores: we get the same answer every time, which makes "
        "difficulty colors and validation reproducible. The combined approach "
        "-- LLM for naming, embeddings for ranking -- gets the best of both.")

    # ================ SAFETY / DUPLICATES ================
    pdf.section("Preventing duplicates")

    pdf.qa("How does each teammate prevent duplicates against past NYT puzzles?",
        "Not all five methods check against the 554 past NYT puzzles. Here is "
        "the honest breakdown:")
    pdf.table(
        ["Teammate", "Check vs past NYT puzzles?", "Self-duplicate check"],
        [
            ["Kaiwen",  "YES: 16-word overlap>6 + exact 4-word group match",  "implicit, per-batch"],
            ["Hengkai", "YES: reject if >=3 words overlap past NYT groups",   "anchor-repeat limit + checkpoints"],
            ["Adreama", "No explicit check vs NYT",                            "YES: persistent JSON files"],
            ["Abuzar",  "No explicit check vs NYT",                            "YES: persistent JSON files"],
            ["Burak",   "No explicit check vs NYT",                            "in-memory only (per notebook run)"],
        ],
        widths=[24, 95, 71],
    )
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "The strongest guarantee comes from Kaiwen's pipeline, which enforces "
        "the check both during word selection (skip-and-retry) and as a final "
        "gate. Because Kaiwen's roundtable validator is used as the shared "
        "acceptance step across the team's final merged dataset, any puzzle "
        "that slips through a teammate's own generator still has to pass the "
        "4-word-group match before it lands in the submitted dataset. In that "
        "sense the team-wide submitted dataset IS guarded against NYT "
        "duplication -- via Kaiwen's step -- even when the upstream generator "
        "didn't check.")

    pdf.qa("What about self-duplication across batches?",
        "Four of the five methods have an explicit self-duplication defense. "
        "Adreama and Abuzar persist three files each (used_words.json, "
        "used_categories.json, used_boards.json) that carry state across "
        "sessions. Hengkai's batch runner checkpoints to a JSON file and "
        "resumes without repeating groups. Kaiwen's CFR excludes already-used "
        "words within a puzzle and deduplicates by board signature across "
        "batches. Burak's notebook, the exception, holds its dedup state only "
        "in memory -- a repeated notebook run can in principle regenerate the "
        "same puzzle. In practice our merged dataset is deduplicated by board "
        "signature as a final step, which removes any cross-teammate "
        "collisions.")

    pdf.qa("What about near-duplicates -- a puzzle with 5 overlapping words?",
        "Kaiwen's threshold is 6 (any overlap of 7 or more words flags the "
        "puzzle; Hengkai's threshold for yellow groups alone is 3). With "
        "16-word puzzles drawn from a 14,877-word bank, overlapping 5 or 6 "
        "words happens by chance perhaps once in thousands of generated "
        "puzzles. The per-puzzle metadata we save includes the overlap count "
        "against each past NYT puzzle so a reviewer can audit this directly "
        "and adjust the threshold if desired.")

    pdf.qa("Could the LLM leak a memorized NYT puzzle?",
        "The underlying language models were trained on web text, so they have "
        "certainly seen Connections discussions. Three of our pipelines "
        "(Kaiwen, Burak, Hengkai) do not let the LLM produce the final word "
        "list directly -- they only let it propose category names or bless a "
        "candidate group, while the actual words come from deterministic "
        "dictionary lookup. For the pipelines that do ask the LLM to emit the "
        "full 16 words (Adreama and Abuzar), the group-level dedup in our "
        "merged pipeline catches any leaked group before acceptance.")

    # ================ QUALITY ================
    pdf.section("Quality and evaluation")

    pdf.qa("99% pass rate -- doesn't that mean your solver is too lenient?",
        "We don't trust a single solver; that's why Kaiwen's pipeline runs TWO "
        "independent ones. A puzzle is accepted only if at least one solver "
        "fully recovers the intended 4-group partition. Both solvers use "
        "deterministic algorithms (greedy cosine selection and beam-search "
        "clustering) and solve only 2-3% of the real NYT puzzles when tested "
        "directly on them -- they are conservative, not easy. So a puzzle that "
        "our solvers CAN crack has a cleanly recoverable structure (exactly "
        "what a good puzzle should have).")

    pdf.qa("How close to the NYT style are the generated puzzles?",
        "We have not yet run a formal human evaluation. Internally, on the "
        "categories where our methods excel (synonyms, types-of-X, themed "
        "nouns) many puzzles are difficult to distinguish from NYT output on "
        "casual inspection. On pure wordplay categories ('___FISH,' letter "
        "homophones), the output is weaker -- see the limitations section. "
        "We added a thumbs-up/thumbs-down rating button to the web app so "
        "real players can rate puzzles at scale, and we plan to collect at "
        "least several hundred ratings before submission.")

    pdf.qa("What's the unique-solution guarantee?",
        "A Connections puzzle is only valid if exactly one 4-way partition "
        "fits the intended themes. Our pipeline enforces this in two ways: "
        "(1) during generation, CFR's candidate selector skips any 4-word "
        "group with a high cross-group 'bleed' score (words that fit another "
        "group too well), and (2) during validation, our two solvers must "
        "find the intended partition -- if they find a DIFFERENT partition "
        "that also satisfies the themes, the puzzle is rejected as ambiguous.")

    pdf.qa("Is the word bank big enough?",
        "The NYT has used about 4,918 unique words across all 554 of its "
        "puzzles. Kaiwen's augmented bank has 14,877 WORDS -- three times "
        "larger. In the CFR output, 62-69% of generated words come from the "
        "NON-NYT portion, showing the expansion is actually being used. "
        "Burak and Hengkai additionally pull from WordNet, ConceptNet, and "
        "the Brown corpus, which expand the vocabulary further within those "
        "specialized pipelines.")

    # ================ COST & SCALE ================
    pdf.section("Cost and scale")

    pdf.qa("What does it cost to generate 10,000 puzzles with each method?",
        "Approximate cost per 10,000 puzzles:")
    pdf.table(
        ["Method", "Approx cost / 10,000 puzzles"],
        [
            ["Kaiwen CFR Mode A (no AI calls)",         "$0"],
            ["Kaiwen CFR Mode B (1 AI call each)",      "~$3"],
            ["Hengkai yellow generator (no AI calls)",  "$0"],
            ["Burak pattern-builder (2 AI calls each)", "~$20"],
            ["Adreama iterative (1 long AI call each)", "~$10"],
            ["Abuzar agent system (1 long AI call)",    "~$15"],
            ["Pipeline A baseline (5 AI calls each)",   "~$50"],
        ],
        widths=[130, 60],
    )
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "The cheapest methods let us generate unlimited puzzles at zero cost; "
        "even the most expensive is within a routine student budget.")

    pdf.qa("Why are different methods cheaper than others?",
        "They make fewer calls to the paid AI service. Pipeline A asks the AI "
        "five times per puzzle. Adreama and Abuzar each make one long call. "
        "CFR Mode B makes one short call. CFR Mode A and Hengkai's generator "
        "make zero calls -- they use dictionaries, embeddings, and math, "
        "which run free on a laptop.")

    pdf.qa("Will this scale to 100,000 puzzles?",
        "Yes. CFR Mode A runs at about 1.3 seconds per puzzle on a single "
        "laptop CPU with no network calls, so 100,000 puzzles take about 36 "
        "hours of wall time and cost $0. Hengkai's batch generator scales "
        "similarly. The bottleneck at that scale is the roundtable validator, "
        "not generation.")

    # ================ REPRODUCIBILITY ================
    pdf.section("Reproducibility")

    pdf.qa("Can someone else reproduce your results without API keys?",
        "Mostly, yes. Kaiwen's code ships with a DRY_RUN=true default: every "
        "call to the AI service is intercepted and replaced by a realistic "
        "mock response. The master notebook, the web app, the test suite, "
        "and the solver benchmark all run end-to-end with no keys configured. "
        "Setting DRY_RUN=false (with OPENAI_API_KEY) switches to real calls. "
        "Adreama's and Abuzar's generators require live API access. Burak's "
        "and Hengkai's generators run offline after pre-computing their "
        "embeddings and corpora.")

    pdf.qa("How do I re-run the benchmarks?",
        "Two commands for Kaiwen's pipeline:")
    pdf.set_font("Courier", "", 9)
    pdf.set_x(14)
    pdf.multi_cell(186, 5,
        "python scripts/cfr/generate_cfr.py --mode remix --count 100\n"
        "python scripts/cfr/generate_cfr.py --mode fresh --count 100")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(10)
    pdf.multi_cell(190, 4.5,
        "Output is written to data/generated/cfr/... with per-puzzle metadata "
        "(pass rate, solver traces, dedup results) for audit. Other "
        "teammates' generators live in their own folders and each ship with "
        "instructions.")

    pdf.qa("Where is the code?",
        "The primary repository is at "
        "https://github.com/Kevin2330/nyt-connections-generator. The live web "
        "app at kevin2330.github.io/nyt-connections-generator/ loads 540+ "
        "validated puzzles from the same repo. Individual teammate code lives "
        "in the STA561/ directory of the submission; Abuzar's code "
        "additionally lives in a private team repository.")

    # ================ LIMITATIONS ================
    pdf.section("Limitations")

    pdf.qa("What's the biggest weakness of the overall system?",
        "Wordplay and syntactic categories. Our embedding-based methods "
        "(Kaiwen, Hengkai) rely on semantic similarity, which captures "
        "'SYNONYMS FOR SMART' but not 'WORDS THAT END IN -ING' or '___FISH.' "
        "These pattern-based categories require string-level and phonetic "
        "reasoning that embeddings don't naturally do well. Burak's CMU-rhyme "
        "green generator and Abuzar's multi-agent system partly address this, "
        "but the hardest (purple) categories remain our collective weakest "
        "output.")

    pdf.qa("Why does WordNet sometimes return awkward words (e.g., MORPHOPHONEMIC)?",
        "WordNet includes many archaic and technical words. Kaiwen's pipeline "
        "filters by corpus frequency and character length, but some oddities "
        "slip through. A higher frequency threshold or intersection with a "
        "common-English list (the Google 10,000-most-common-words list is "
        "already included as an optional filter) would tighten this further.")

    pdf.qa("Why does Burak's generator have no cross-session deduplication?",
        "It is an honest gap. Burak's notebook holds its used-words set only "
        "in memory, so two separate notebook runs could in principle generate "
        "the same puzzle. In practice the final merged dataset is "
        "deduplicated by 16-word board signature as a post-processing step, "
        "which removes any such collisions before submission.")

    # ================ TEAMWORK ================
    pdf.section("Teamwork")

    pdf.qa("Who did what?", "")
    pdf.table(
        ["Teammate", "Contribution"],
        [
            ["Adreama", "Iterative AI generator with cross-session memory and trap-word webs"],
            ["Burak",   "Non-AI pattern-driven builder (purple mechanism + rhyme green + word2vec yellow)"],
            ["Hengkai", "Yellow specialist: embedding + ConceptNet scoring, NYT-history overlap check"],
            ["Kaiwen",  "Pipeline A baseline, CFR Modes A & B, roundtable validator, web app"],
            ["Abuzar",  "Multi-agent critic system + Flask web server + concept-inspiration library"],
        ],
        widths=[25, 165],
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
