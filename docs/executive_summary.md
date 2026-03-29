# Infinite Connections — Executive Summary

## Overview

Infinite Connections is an AI system that generates NYT-style Connections puzzles at scale. The system combines large language model creativity (Claude, Anthropic) with embedding-based validation (MPNET) to produce puzzles that are diverse, solvable, and appropriately challenging.

## Problem

The NYT Connections puzzle requires players to sort 16 words into 4 groups of 4 based on hidden connections. Creating these puzzles manually requires significant creative effort — each puzzle must have exactly one valid solution among millions of possible groupings, with a carefully calibrated difficulty gradient.

## Approach

Our three-stage pipeline:

1. **Generation**: Claude API generates word groups using story injection for diversity and a false-group method for deception. MPNET embeddings select the most cohesive 4 words from 8-word candidate pools, replacing unreliable LLM self-selection.

2. **Validation**: Two independent solvers (embedding-based greedy and clustering-based beam search) verify each puzzle has a unique solution. Puzzles where solvers disagree are flagged as ambiguous and discarded.

3. **Quality Control**: Cosine similarity thresholds assign difficulty colors (yellow through purple), and deduplication checks prevent overlap with existing NYT puzzles.

## Results

- Generated [N] candidate puzzles with a [X]% validation pass rate
- Solver agreement serves as an effective quality gate for puzzle uniqueness
- False-group puzzles are rated most engaging in preliminary evaluation
- MPNET-based word selection produces consistent difficulty calibration

## Deliverables

- Reproducible Jupyter notebook demonstrating the full pipeline
- Playable web interface serving generated puzzles
- Dataset of validated puzzles with quality metrics

---

*STA 561D — Duke University*
