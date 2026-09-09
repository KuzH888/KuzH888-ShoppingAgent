"""Command-line entry point for reproducible project evaluation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evaluator import evaluate_project, render_markdown_report


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate KuzH888-ShoppingAgent")
    parser.add_argument("--label", choices=["development-baseline", "final"], default="development-baseline")
    parser.add_argument("--output", type=Path, default=Path("outputs/evaluation_baseline.md"))
    args = parser.parse_args()

    report = evaluate_project(label=args.label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_markdown_report(report), encoding="utf-8")
    json_path = args.output.with_suffix(".json")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Evaluation report: {args.output}")
    print(f"Machine-readable results: {json_path}")
    print(f"Overall pass rate: {report['metrics']['overall_pass_rate_pct']:.2f}%")


if __name__ == "__main__":
    main()
