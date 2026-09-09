"""Tests for parsing, filtering, ranking, fallback, and comparison."""

import json
from pathlib import Path

import pytest

from src.services import RecommendationEngine, parse_customer_need
from src.tools import CompareProductsTool, ProductDetailsTool, SearchProductsTool
from src.utils.catalog import load_catalog


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def engine():
    return RecommendationEngine(load_catalog())


def test_bilingual_recommendation_cases(engine):
    cases = json.loads(
        (PROJECT_ROOT / "data" / "test_cases.json").read_text(encoding="utf-8")
    )
    for case in cases:
        result = engine.recommend(parse_customer_need(case["query"]))
        assert result.status == case["expected_status"], case["id"]
        if case["expected_top_product"] is not None:
            assert result.recommendations[0].product_id == case["expected_top_product"], case["id"]


def test_hard_budget_constraint_is_never_relaxed(engine):
    need = parse_customer_need("我必须买50澳元以内带主动降噪的头戴式耳机。")
    result = engine.recommend(need)

    assert result.status == "no_exact_match"
    assert not result.recommendations
    assert result.alternatives
    assert "over_budget" in result.alternatives[0].violations


def test_top_three_order_is_stable(engine):
    need = parse_customer_need("推荐适合通勤的轻便产品。")
    first = engine.recommend(need).model_dump()
    second = engine.recommend(need).model_dump()

    assert first == second
    assert len(first["recommendations"]) == 3


def test_comparison_rejects_unknown_product(engine):
    with pytest.raises(ValueError, match="Unknown product ID"):
        engine.compare(["DIG-001", "BAD-999"])


def test_helloagents_tools_return_structured_data():
    search_response = SearchProductsTool().run(
        {"query": "100澳元以内适合通勤且降噪很重要的耳机"}
    )
    detail_response = ProductDetailsTool().run({"product_id": "DIG-001"})
    compare_response = CompareProductsTool().run(
        {"product_ids": ["DIG-001", "DIG-003"], "language": "zh"}
    )

    assert search_response.data["status"] == "matched"
    assert search_response.data["recommendations"][0]["product_id"] == "DIG-001"
    assert detail_response.data["id"] == "DIG-001"
    assert len(compare_response.data["products"]) == 2
