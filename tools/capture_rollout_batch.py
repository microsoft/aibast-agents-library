#!/usr/bin/env python3
"""Capture missing solution transcript corpora sequentially."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture_demo_transcripts import DEFAULT_BRAINSTEM_AGENTS, REPO, capture


CASES = REPO / "tests" / "demo_cases"


def case_paths(slugs, all_missing):
    if all_missing:
        paths = sorted(CASES.glob("*.json"))
        return [
            path
            for path in paths
            if not (
                REPO / "solutions" / path.stem / "evals" / "transcripts.json"
            ).exists()
        ]
    return [CASES / f"{slug}.json" for slug in slugs]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--all-missing", action="store_true")
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=DEFAULT_BRAINSTEM_AGENTS,
    )
    args = parser.parse_args()
    if not args.slugs and not args.all_missing:
        parser.error("provide solution slugs or --all-missing")

    paths = case_paths(args.slugs, args.all_missing)
    missing = [path for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(", ".join(str(path) for path in missing))

    results = []
    failures = []
    for case_path in paths:
        output = REPO / "solutions" / case_path.stem / "evals" / "transcripts.json"
        try:
            artifact = capture(
                case_path.resolve(),
                output.resolve(),
                args.agents_dir.expanduser().resolve(),
            )
        except Exception as error:
            if not args.continue_on_error:
                raise
            failures.append({"slug": case_path.stem, "error": str(error)})
            print(f"[FAIL] {case_path.stem}: {error}")
            continue
        results.append(
            {
                "slug": case_path.stem,
                "solution": artifact["solution"],
                "cases": len(artifact["transcripts"]),
            }
        )
        print(f"[OK] {case_path.stem}: {len(artifact['transcripts'])} cases")

    print(json.dumps({"captured": results, "failures": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
