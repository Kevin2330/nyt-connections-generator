"""Split generated puzzles into separate files by difficulty color.

Usage:
    python scripts/split_by_color.py --input-dir data/generated/batch_575/
"""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Split puzzles by color")
    parser.add_argument("--input-dir", required=True, help="Directory with *_valid.json files")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    valid_files = list(input_dir.glob("*_valid.json"))

    if not valid_files:
        print(f"No *_valid.json files found in {input_dir}")
        return

    # Load all valid puzzles
    all_puzzles = []
    for f in valid_files:
        with open(f) as fh:
            puzzles = json.load(fh)
            all_puzzles.extend(puzzles)
            print(f"Loaded {len(puzzles)} puzzles from {f.name}")

    print(f"Total valid puzzles: {len(all_puzzles)}")

    # Bucket groups by color
    buckets = {"yellow": [], "green": [], "blue": [], "purple": []}

    for puzzle in all_puzzles:
        for group in puzzle["groups"]:
            color = group.get("color", "unknown")
            if color in buckets:
                buckets[color].append({
                    "category": group["category"],
                    "words": group["words"],
                    "color": color,
                    "similarity_score": group.get("similarity_score", 0.0),
                    "source_puzzle_id": puzzle["id"],
                })

    # Write per-color files
    for color, groups in buckets.items():
        out_path = input_dir / f"{color}_groups.json"
        with open(out_path, "w") as f:
            json.dump(groups, f, indent=2)

        word_count = sum(len(g["words"]) for g in groups)
        print(f"  {color:>6}: {len(groups)} groups, {word_count} words -> {out_path.name}")

    print(f"\nDone! Files written to {input_dir}")


if __name__ == "__main__":
    main()
