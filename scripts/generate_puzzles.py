"""Generate puzzles with a real LLM and validate them.

Usage:
    # Generate 10 puzzles with GPT-4o-mini (cheapest):
    export DRY_RUN=false
    export OPENAI_API_KEY=sk-...
    python scripts/generate_puzzles.py --count 10

    # Generate with Claude instead:
    export DRY_RUN=false
    export LLM_PROVIDER=anthropic
    export ANTHROPIC_API_KEY=sk-ant-...
    python scripts/generate_puzzles.py --count 10

    # Use false-group method (higher quality):
    python scripts/generate_puzzles.py --count 10 --method false_group
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import DRY_RUN, LLM_PROVIDER, GENERATED_PUZZLES_PATH
from src.llm_client import LLMClient
from src.generator.pipeline import PuzzlePipeline
from src.solvers.roundtable import Roundtable


def main():
    parser = argparse.ArgumentParser(description="Generate Connections puzzles")
    parser.add_argument("--count", type=int, default=10, help="Number of puzzles to generate")
    parser.add_argument("--method", choices=["iterative", "false_group"], default="iterative")
    parser.add_argument("--validate", action="store_true", default=True,
                        help="Run roundtable validation (default: yes)")
    parser.add_argument("--no-validate", dest="validate", action="store_false")
    parser.add_argument("--output-dir", type=str, default=None,
                        help="Custom output directory (default: data/generated/)")
    args = parser.parse_args()

    print(f"DRY_RUN:   {DRY_RUN}")
    print(f"Provider:  {LLM_PROVIDER}")
    print(f"Method:    {args.method}")
    print(f"Count:     {args.count}")
    print(f"Validate:  {args.validate}")
    print()

    if DRY_RUN:
        print("WARNING: DRY_RUN=true, using mock LLM. Set DRY_RUN=false for real generation.")
        print()

    # Load embedding model (needed for MPNET selection + solvers)
    print("Loading MPNET model...")
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("all-mpnet-base-v2")

    # Load word bank from NYT data
    word_bank = []
    nyt_path = PROJECT_ROOT / "data" / "nyt_puzzles" / "ConnectionsFinalDataset (1).json"
    if nyt_path.exists():
        with open(nyt_path) as f:
            nyt = json.load(f)
        word_bank = list(set(w.upper() for p in nyt for w in p["words"]))
        print(f"Word bank: {len(word_bank)} words from NYT dataset")
    else:
        word_bank = ["RAIN", "SUN", "MOON", "STAR", "TREE", "LAKE", "BIRD", "FISH",
                     "ROCK", "WAVE", "SAND", "WIND", "FIRE", "SNOW", "LEAF", "SEED"]
        print(f"Word bank: {len(word_bank)} fallback words (NYT data not found)")

    # Initialize pipeline
    llm = LLMClient()
    pipeline = PuzzlePipeline(llm=llm, embedding_model=model, word_bank=word_bank)
    roundtable = Roundtable(embedding_model=model) if args.validate else None

    # Generate
    results = {"valid": [], "invalid": [], "errors": []}
    start = time.time()

    for i in range(args.count):
        t0 = time.time()
        print(f"\n--- Puzzle {i+1}/{args.count} ---")

        try:
            puzzle = pipeline.generate(method=args.method)
            elapsed = time.time() - t0
            print(f"Generated in {elapsed:.1f}s: {puzzle['id']}")

            for g in puzzle["groups"]:
                print(f"  [{g['color']:>6}] {g['category']}: {', '.join(g['words'])} "
                      f"(sim={g['similarity_score']:.3f})")

            if roundtable:
                val = roundtable.validate(puzzle)
                puzzle["metadata"]["solver_agreement"] = val["solver_agreement"]
                puzzle["metadata"]["solvers_used"] = val["solvers_used"]
                puzzle["metadata"]["solver_results"] = val["solver_results"]

                emb_c = val["groups_correct"].get("embedding", 0)
                clust_c = val["groups_correct"].get("clustering", 0)
                # Relaxed acceptance: any solver fully solving = puzzle has a findable solution
                accept = (emb_c == 4) or (clust_c == 4)
                puzzle["metadata"]["accepted"] = accept
                print(f"  Validation: {'VALID' if accept else 'INVALID'} "
                      f"(emb={emb_c}/4, clust={clust_c}/4, agree={val['solver_agreement']})")

                if accept:
                    results["valid"].append(puzzle)
                else:
                    results["invalid"].append(puzzle)
            else:
                results["valid"].append(puzzle)

        except Exception as e:
            print(f"  ERROR: {e}")
            results["errors"].append({"index": i, "error": str(e)})

    total_time = time.time() - start

    # Save results
    out_dir = Path(args.output_dir) if args.output_dir else Path(GENERATED_PUZZLES_PATH)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    def _json_default(obj):
        # Handle numpy scalars, frozensets, and other non-serializable types
        if hasattr(obj, "item"):
            return obj.item()
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        return str(obj)

    if results["valid"]:
        valid_path = out_dir / f"puzzles_{timestamp}_valid.json"
        with open(valid_path, "w") as f:
            json.dump(results["valid"], f, indent=2, default=_json_default)
        print(f"\nSaved {len(results['valid'])} valid puzzles to {valid_path}")

    if results["invalid"]:
        invalid_path = out_dir / f"puzzles_{timestamp}_invalid.json"
        with open(invalid_path, "w") as f:
            json.dump(results["invalid"], f, indent=2, default=_json_default)
        print(f"Saved {len(results['invalid'])} invalid puzzles to {invalid_path}")

    # Summary
    print(f"\n{'='*50}")
    print(f"GENERATION SUMMARY")
    print(f"{'='*50}")
    print(f"Total time:     {total_time:.1f}s ({total_time/args.count:.1f}s per puzzle)")
    print(f"Generated:      {len(results['valid']) + len(results['invalid'])}")
    print(f"Valid:          {len(results['valid'])}")
    print(f"Invalid:        {len(results['invalid'])}")
    print(f"Errors:         {len(results['errors'])}")
    if results["valid"] or results["invalid"]:
        pass_rate = len(results["valid"]) / (len(results["valid"]) + len(results["invalid"]))
        print(f"Pass rate:      {pass_rate:.0%}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
