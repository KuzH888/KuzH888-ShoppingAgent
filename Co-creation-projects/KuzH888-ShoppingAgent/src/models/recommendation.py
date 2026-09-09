"""Models used by the deterministic recommendation pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class CustomerNeed(BaseModel):
    """Structured customer needs extracted from Chinese or English text."""

    model_config = ConfigDict(extra="forbid")

    original_query: str = Field(min_length=1)
    language: Literal["zh", "en"]
    target_subcategories: list[str] = Field(default_factory=list)
    budget_max: float | None = Field(default=None, gt=0)
    use_cases: list[str] = Field(default_factory=list)
    must_have: list[str] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)
    excluded_features: list[str] = Field(default_factory=list)
    preferred_colors: list[str] = Field(default_factory=list)
    excluded_colors: list[str] = Field(default_factory=list)


class ScoredProduct(BaseModel):
    """One ranked product and its explainable score components."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    name: str
    price: float
    currency: str
    score: float = Field(ge=0, le=100)
    score_breakdown: dict[str, float]
    matched_requirements: list[str]
    tradeoffs: list[str]


class NearMatch(BaseModel):
    """A fallback product that violates one or more hard constraints."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    name: str
    price: float
    currency: str
    score: float = Field(ge=0, le=100)
    violations: list[str]


class RecommendationResult(BaseModel):
    """Deterministic recommendation result returned to tools and APIs."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["matched", "no_exact_match"]
    need: CustomerNeed
    recommendations: list[ScoredProduct] = Field(default_factory=list)
    alternatives: list[NearMatch] = Field(default_factory=list)
    message: str
