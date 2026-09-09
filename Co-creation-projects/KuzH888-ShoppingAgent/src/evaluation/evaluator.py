"""Repeatable, API-free evaluation of catalogue-grounded assistant behaviour."""

from __future__ import annotations

import hashlib
import json
import math
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.agents import ShoppingAssistant
from src.services import PolicyService, RecommendationEngine, parse_customer_need
from src.utils.catalog import DEFAULT_CATALOG_PATH, load_catalog


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = PROJECT_ROOT / "data" / "evaluation_cases.json"


def _percentage(passed: int, total: int) -> float:
    return round(passed / total * 100, 2) if total else 0.0


def _catalogue_fingerprint(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * 0.95) - 1)]


def evaluate_project(
    cases_path: Path = DEFAULT_CASES_PATH,
    catalogue_path: Path = DEFAULT_CATALOG_PATH,
    *,
    label: str = "development-baseline",
) -> dict[str, Any]:
    """Evaluate deterministic behaviour without contacting an external LLM."""
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    catalog = load_catalog(catalogue_path)
    engine = RecommendationEngine(catalog)
    assistant = ShoppingAssistant(engine)
    policies = PolicyService()
    products_by_id = {product.id: product for product in catalog.products}

    rows: list[dict[str, Any]] = []
    recommendation_checks: list[bool] = []
    constraint_checks: list[bool] = []
    grounding_checks: list[bool] = []
    language_checks: list[bool] = []
    latencies: list[float] = []

    for case in cases:
        started = time.perf_counter()
        if case["kind"] == "recommendation":
            need = parse_customer_need(case["query"])
            result = engine.recommend(need)
            actual_top = result.recommendations[0].product_id if result.recommendations else None
            expected_ok = (
                result.status == case["expected_status"]
                and actual_top == case["expected_top_product"]
            )
            if result.recommendations:
                constraints_ok = all(
                    not engine.hard_constraint_violations(need, products_by_id[item.product_id])
                    for item in result.recommendations
                )
            else:
                constraints_ok = bool(result.alternatives) and all(
                    item.violations for item in result.alternatives
                )
            grounding_ok = all(
                item.product_id in products_by_id
                and item.price == products_by_id[item.product_id].price
                for item in [*result.recommendations, *result.alternatives]
            )
            language_ok = need.language == case["expected_language"]
            actual = result.status
            recommendation_checks.append(expected_ok)
            constraint_checks.append(constraints_ok)
        else:
            reply = assistant.chat(case["query"], session_id=f"eval-{case['id']}")
            expected_ok = reply.type == case["expected_reply_type"]
            language_ok = reply.language == case["expected_language"]
            actual = reply.type
            if reply.type == "product_details":
                product = reply.facts.get("product", {})
                expected_ids = case["expected_product_ids"]
                grounding_ok = (
                    product.get("id") in expected_ids
                    and product == products_by_id[product["id"]].model_dump(mode="json")
                )
            elif reply.type == "comparison":
                compared = reply.facts.get("products", [])
                actual_ids = [item.get("product_id") for item in compared]
                grounding_ok = actual_ids == case["expected_product_ids"] and all(
                    item["price"] == products_by_id[item["product_id"]].price
                    for item in compared
                )
            elif reply.type == "policy":
                policy = reply.facts.get("policy", {})
                expected_policy = policies.get(case["expected_policy_id"])
                grounding_ok = policy == expected_policy.model_dump(mode="json")
            else:
                grounding_ok = False

        latency_ms = (time.perf_counter() - started) * 1000
        latencies.append(latency_ms)
        grounding_checks.append(grounding_ok)
        language_checks.append(language_ok)
        passed = expected_ok and grounding_ok and language_ok
        if case["kind"] == "recommendation":
            passed = passed and constraints_ok
        rows.append(
            {
                "id": case["id"],
                "kind": case["kind"],
                "passed": passed,
                "actual": actual,
                "latency_ms": round(latency_ms, 3),
            }
        )

    passed_count = sum(row["passed"] for row in rows)
    return {
        "label": label,
        "is_final": label == "final",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "offline-simulation",
        "catalogue_sha256": _catalogue_fingerprint(catalogue_path),
        "catalogue_version": catalog.version,
        "product_count": len(catalog.products),
        "case_count": len(rows),
        "metrics": {
            "overall_pass_rate_pct": _percentage(passed_count, len(rows)),
            "recommendation_expected_result_pct": _percentage(sum(recommendation_checks), len(recommendation_checks)),
            "hard_constraint_satisfaction_pct": _percentage(sum(constraint_checks), len(constraint_checks)),
            "catalogue_grounding_pct": _percentage(sum(grounding_checks), len(grounding_checks)),
            "language_consistency_pct": _percentage(sum(language_checks), len(language_checks)),
            "average_latency_ms": round(sum(latencies) / len(latencies), 3),
            "p95_latency_ms": round(_percentile_95(latencies), 3),
        },
        "cases": rows,
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    """Create a human-readable report suitable for the GitHub submission."""
    title = "Final Evaluation" if report["is_final"] else "Development Baseline Evaluation"
    warning = "" if report["is_final"] else "> This is a development baseline. Re-run after replacing products and images; it is not the final submission score.\n\n"
    metrics = report["metrics"]
    lines = [
        f"# {title}",
        "",
        warning.rstrip(),
        "",
        "## Evaluation context",
        "",
        f"- Mode: `{report['mode']}`",
        f"- Cases: {report['case_count']}",
        f"- Products: {report['product_count']}",
        f"- Catalogue version: `{report['catalogue_version']}`",
        f"- Catalogue SHA-256: `{report['catalogue_sha256']}`",
        f"- Generated at: `{report['generated_at']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Overall case pass rate | {metrics['overall_pass_rate_pct']:.2f}% |",
        f"| Expected recommendation result | {metrics['recommendation_expected_result_pct']:.2f}% |",
        f"| Hard-constraint satisfaction | {metrics['hard_constraint_satisfaction_pct']:.2f}% |",
        f"| Catalogue grounding | {metrics['catalogue_grounding_pct']:.2f}% |",
        f"| Language consistency | {metrics['language_consistency_pct']:.2f}% |",
        f"| Average local latency | {metrics['average_latency_ms']:.3f} ms |",
        f"| P95 local latency | {metrics['p95_latency_ms']:.3f} ms |",
        "",
        "## Case results",
        "",
        "| Case | Type | Passed | Actual result | Latency |",
        "|---|---|:---:|---|---:|",
    ]
    for row in report["cases"]:
        lines.append(
            f"| {row['id']} | {row['kind']} | {'Yes' if row['passed'] else 'No'} | "
            f"{row['actual']} | {row['latency_ms']:.3f} ms |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "These measurements cover deterministic simulation behaviour. They do not measure live LLM response quality or network latency. The final report must be regenerated after catalogue edits and live-provider testing.",
            "",
        ]
    )
    return "\n".join(line for line in lines if line is not None)
