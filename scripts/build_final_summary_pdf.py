"""Build the 2-page team executive summary PDF via fpdf2."""

import sys
from pathlib import Path
from fpdf import FPDF

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT = PROJECT_ROOT / "docs" / "final_executive_summary.pdf"


class ExecSummary(FPDF):
    def header(self):
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(95, 5, "Infinite Connections -- Executive Summary", align="L")
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
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(26, 84, 144)
        self.ln(1)
        self.cell(0, 6, title, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(0, 0, 0)
        self.ln(0.5)

    def body(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(10)
        self.multi_cell(190, 4.5, text)
        self.ln(0.5)

    def bullet(self, name, text):
        self.set_font("Helvetica", "B", 10)
        self.set_x(10)
        self.multi_cell(190, 4.5, f"  -  {name}")
        self.set_font("Helvetica", "", 10)
        self.set_x(14)
        self.multi_cell(186, 4.5, text)
        self.ln(0.5)

    def keybox(self, text):
        self.ln(1)
        y = self.get_y()
        self.set_fill_color(255, 248, 220)
        self.set_draw_color(220, 170, 50)
        self.set_font("Helvetica", "", 10)
        lines_est = len(text) // 90 + 3
        h = max(14, lines_est * 4.5 + 4)
        self.rect(10, y, 190, h, style="DF")
        self.set_xy(14, y + 2)
        self.multi_cell(182, 4.5, text)
        self.ln(1)


def build():
    pdf = ExecSummary(orientation="P", unit="mm", format="Letter")
    pdf.set_margins(10, 12, 10)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(26, 84, 144)
    pdf.ln(2)
    pdf.cell(0, 8, "Infinite Connections", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 5, "Generating New NYT-Style Word Puzzles at Scale",
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

    pdf.section("The problem")
    pdf.body(
        "The New York Times Connections puzzle shows the player 16 words and "
        "asks them to sort the words into 4 groups of 4 based on a hidden theme. "
        "The themes can be simple (four synonyms for \"hello\"), tricky (four "
        "things that fit before the word \"fish\"), or outright playful (four "
        "Taylor Swift album titles). For this project we built a system that "
        "CREATES these puzzles automatically, at scale, with a web app that "
        "lets anyone play them in the browser."
    )
    pdf.body(
        "Generating a good Connections puzzle is harder than it looks. The 16 "
        "words must fit together in exactly one way -- no ambiguity. The themes "
        "must feel fresh but recognizable. And we cannot accidentally reproduce "
        "a puzzle the NYT has already published, which the grading rubric treats "
        "as an automatic failure."
    )

    pdf.section("What we built -- five complementary methods")
    pdf.body(
        "Rather than pick one approach and hope it works, each teammate built a "
        "different method. Together they cover the full design space from \"ask "
        "the AI everything\" to \"use no AI at all.\""
    )

    pdf.bullet("Adreama -- Iterative AI generation.",
        "Asks the AI to build one group at a time, remembering what it has "
        "already used. Built up a library of 400+ puzzles with memory that "
        "persists across sessions, so duplicates never creep in even across "
        "many runs.")
    pdf.bullet("Burak -- Pattern-driven dictionary builder.",
        "Uses no AI for generation. Instead, pulls words from language "
        "databases (WordNet, ConceptNet, Datamuse) and fills puzzle slots using "
        "explicit patterns (synonyms, category membership, shared actions). "
        "Specializes in the green and blue difficulty levels with thousands of "
        "candidate groups.")
    pdf.bullet("Hengkai -- Quality-first yellow specialist.",
        "Focused on the easiest (yellow) difficulty, where cohesion and "
        "obviousness matter most. Uses cached word embeddings and strict filters "
        "that throw out any word too obscure or technical.")
    pdf.bullet("Kaiwen -- Two pipelines, compared head to head.",
        "Pipeline A follows the published 'Making New Connections' paper: five "
        "AI calls per puzzle. Pipeline B is our new method, CATEGORY-FIRST "
        "RETRIEVAL (CFR): the AI proposes only the category names (one call per "
        "puzzle, or zero if we reuse NYT categories), then math finds the "
        "matching words from an expanded 14,877-word dictionary.")
    pdf.bullet("Abuzar -- Multi-agent critic system.",
        "Builds puzzles with one AI agent and has a second agent critique the "
        "result. Good ideas survive, bad ones get rewritten. Pairs this with a "
        "playable web server and a library of 'concept inspirations' to keep "
        "themes fresh.")

    pdf.ln(1)
    pdf.body(
        "Individual generators use different duplicate-prevention strategies: "
        "Kaiwen and Hengkai check each candidate against the 554 past NYT "
        "puzzles directly; the other three guard against SELF-repetition via "
        "persistent memory files but don't check the NYT corpus. As a final "
        "gate, every puzzle in our MERGED submitted dataset is passed through "
        "Kaiwen's shared validator, which flags any 16-word set that shares "
        "more than six words with a past NYT puzzle AND any 4-word group that "
        "exactly matches a past NYT group. That merged gate is what "
        "guarantees our submitted dataset cannot reproduce a past puzzle."
    )

    pdf.section("Results")
    pdf.keybox(
        "Across all methods we generated roughly 2,000+ validated puzzles. The "
        "best pipeline (CFR) achieves a 99% pass rate on automated validation, "
        "reproduces ZERO past NYT puzzles, and uses words from a 14,877-word "
        "vocabulary -- three times larger than the NYT original. At full scale, "
        "generating 10,000 puzzles costs between $0 and $50 depending on the "
        "method, so we can produce as many as the course requires."
    )

    pdf.section("What we learned")
    pdf.body(
        "The surprising finding was that the simplest, least-AI-heavy method "
        "produced the highest pass rate. Asking the AI to do everything (pick "
        "words, pick categories, pick difficulty) is both expensive and "
        "unreliable: the AI gives inconsistent word choices and needs a separate "
        "editor pass to clean up. But letting a language AI do only THE CREATIVE "
        "NAMING step -- and letting math handle the mechanical word-lookup step "
        "-- produces better results at one-twentieth the cost and four times the "
        "speed."
    )
    pdf.body(
        "Across the team, the strongest puzzles tended to come from methods "
        "that combined an AI's creativity with deterministic math for selection: "
        "everyone's pipeline used embeddings (a way to compare how similar two "
        "words are numerically) somewhere in the process."
    )

    pdf.section("Deliverables")
    pdf.bullet("Live web app",
        "kevin2330.github.io/nyt-connections-generator/ loads 540+ validated "
        "puzzles in the NYT Connections interface. Anyone can play them in a "
        "browser.")
    pdf.bullet("Master Jupyter notebook",
        "notebooks/master_demo.ipynb walks through every method end-to-end in "
        "reproducible form. It runs without any API keys -- all AI calls fall "
        "back to realistic mock responses when none are configured.")
    pdf.bullet("Technical report",
        "Methods document and per-teammate folders detail the algorithms, math, "
        "and benchmarks.")
    pdf.bullet("Pre-generated dataset",
        "A large set of validated puzzles on disk, from which the course can "
        "sample for TA evaluation.")

    pdf.section("Future work")
    pdf.body(
        "The next step is HUMAN evaluation, not just the automated solvers: put "
        "the puzzles in front of real puzzle players and measure how many they "
        "would believe came from the NYT. We added a mechanism for that to the "
        "web app (thumbs-up / thumbs-down on each puzzle) but haven't yet "
        "collected a large sample. A stretch goal is a fine-tuned embedding "
        "model trained specifically on Connections puzzles, which would likely "
        "push the pass rate even higher for puzzles built around wordplay (the "
        "one category where our current system is weakest)."
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    build()
