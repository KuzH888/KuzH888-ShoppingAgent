"""Tests for the repeatable offline evaluation pipeline."""

from src.evaluation import evaluate_project, render_markdown_report


def test_development_evaluation_is_complete_and_grounded():
    report = evaluate_project()

    assert report["is_final"] is False
    assert report["case_count"] == 19
    assert len(report["catalogue_sha256"]) == 64
    assert report["metrics"]["overall_pass_rate_pct"] == 100.0
    assert report["metrics"]["hard_constraint_satisfaction_pct"] == 100.0
    assert report["metrics"]["catalogue_grounding_pct"] == 100.0
    assert report["metrics"]["language_consistency_pct"] == 100.0


def test_markdown_report_clearly_marks_non_final_results():
    markdown = render_markdown_report(evaluate_project())

    assert "Development Baseline Evaluation" in markdown
    assert "not the final submission score" in markdown
    assert "Catalogue SHA-256" in markdown
