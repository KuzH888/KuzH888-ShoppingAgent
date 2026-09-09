"""Deterministic filtering, ranking, fallback, and comparison logic."""

from __future__ import annotations

import math

from src.models import (
    CustomerNeed,
    NearMatch,
    Product,
    ProductCatalog,
    RecommendationResult,
    ScoredProduct,
)


class RecommendationEngine:
    """Recommend products without relying on an LLM for facts or arithmetic."""

    def __init__(self, catalog: ProductCatalog):
        self.catalog = catalog
        self._products_by_id = {product.id: product for product in catalog.products}

    @staticmethod
    def _overlap_score(requested: list[str], available: list[str], weight: float) -> float:
        if not requested:
            return weight
        matches = len(set(requested) & set(available))
        return weight * matches / len(set(requested))

    @staticmethod
    def _budget_score(need: CustomerNeed, product: Product) -> float:
        if need.budget_max is None:
            return 10.0
        remaining_ratio = max(0.0, (need.budget_max - product.price) / need.budget_max)
        return 5.0 + 5.0 * remaining_ratio

    @staticmethod
    def _review_confidence(product: Product) -> float:
        return min(math.log1p(product.review_count) / math.log1p(250), 1.0) * 5.0

    def hard_constraint_violations(self, need: CustomerNeed, product: Product) -> list[str]:
        """Return explicit reasons why a product is not an exact match."""
        violations: list[str] = []
        if product.stock <= 0:
            violations.append("out_of_stock")
        if need.target_subcategories and product.subcategory not in need.target_subcategories:
            violations.append("wrong_product_type")
        if need.budget_max is not None and product.price > need.budget_max:
            violations.append("over_budget")

        missing_features = sorted(set(need.must_have) - set(product.features))
        violations.extend(f"missing_feature:{feature}" for feature in missing_features)

        blocked_features = sorted(set(need.excluded_features) & set(product.features))
        violations.extend(f"excluded_feature:{feature}" for feature in blocked_features)

        blocked_colors = sorted(set(need.excluded_colors) & set(product.colors))
        violations.extend(f"excluded_color:{color}" for color in blocked_colors)
        return violations

    def score_product(self, need: CustomerNeed, product: Product) -> ScoredProduct:
        """Score one exact-match candidate using the approved 100-point formula."""
        use_case_score = self._overlap_score(need.use_cases, product.use_cases, 40.0)
        preferences = list(dict.fromkeys(need.preferences + need.preferred_colors))
        available_preferences = product.features + product.colors
        preference_score = self._overlap_score(preferences, available_preferences, 30.0)
        rating_score = product.rating / 5.0 * 15.0
        budget_score = self._budget_score(need, product)
        review_score = self._review_confidence(product)

        breakdown = {
            "use_cases": round(use_case_score, 2),
            "preferences": round(preference_score, 2),
            "rating": round(rating_score, 2),
            "budget": round(budget_score, 2),
            "review_confidence": round(review_score, 2),
        }
        score = round(sum(breakdown.values()), 2)

        matched = []
        matched.extend(sorted(set(need.use_cases) & set(product.use_cases)))
        matched.extend(sorted(set(need.must_have) & set(product.features)))
        matched.extend(sorted(set(need.preferences) & set(product.features)))
        matched.extend(sorted(set(need.preferred_colors) & set(product.colors)))

        tradeoffs = []
        missing_preferences = sorted(set(need.preferences) - set(product.features))
        tradeoffs.extend(f"missing_preference:{item}" for item in missing_preferences)
        if need.preferred_colors and not set(need.preferred_colors) & set(product.colors):
            tradeoffs.append("preferred_colour_unavailable")

        name = product.name.zh if need.language == "zh" else product.name.en
        return ScoredProduct(
            product_id=product.id,
            name=name,
            price=product.price,
            currency=product.currency,
            score=score,
            score_breakdown=breakdown,
            matched_requirements=list(dict.fromkeys(matched)),
            tradeoffs=tradeoffs,
        )

    def recommend(self, need: CustomerNeed, top_k: int = 3) -> RecommendationResult:
        """Return exact matches or clearly labelled near matches."""
        if not 1 <= top_k <= 3:
            raise ValueError("top_k must be between 1 and 3")

        exact_products = [
            product
            for product in self.catalog.products
            if not self.hard_constraint_violations(need, product)
        ]
        scored = [self.score_product(need, product) for product in exact_products]
        scored.sort(key=lambda item: (-item.score, item.price, item.product_id))

        if scored:
            message = (
                "已找到符合硬性条件的商品。"
                if need.language == "zh"
                else "Products matching all hard constraints were found."
            )
            return RecommendationResult(
                status="matched",
                need=need,
                recommendations=scored[:top_k],
                message=message,
            )

        alternatives: list[NearMatch] = []
        candidates = [
            product
            for product in self.catalog.products
            if product.stock > 0
            and (
                not need.target_subcategories
                or product.subcategory in need.target_subcategories
            )
        ]
        for product in candidates:
            scored_product = self.score_product(need, product)
            violations = self.hard_constraint_violations(need, product)
            alternatives.append(
                NearMatch(
                    product_id=product.id,
                    name=scored_product.name,
                    price=product.price,
                    currency=product.currency,
                    score=scored_product.score,
                    violations=violations,
                )
            )
        alternatives.sort(
            key=lambda item: (len(item.violations), -item.score, item.price, item.product_id)
        )
        message = (
            "没有商品满足全部硬性条件；以下备选不会被标记为精确匹配。"
            if need.language == "zh"
            else "No product meets every hard constraint; alternatives are not exact matches."
        )
        return RecommendationResult(
            status="no_exact_match",
            need=need,
            alternatives=alternatives[:2],
            message=message,
        )

    def get_product(self, product_id: str) -> Product:
        """Return one product or raise a clear error."""
        try:
            return self._products_by_id[product_id]
        except KeyError as exc:
            raise ValueError(f"Unknown product ID: {product_id}") from exc

    def compare(self, product_ids: list[str], language: str = "zh") -> list[dict]:
        """Return factual comparison data for two or three products."""
        if not 2 <= len(product_ids) <= 3:
            raise ValueError("Compare two or three products at a time")
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Product IDs must be unique")

        comparison = []
        for product_id in product_ids:
            product = self.get_product(product_id)
            comparison.append(
                {
                    "product_id": product.id,
                    "name": product.name.zh if language == "zh" else product.name.en,
                    "price": product.price,
                    "currency": product.currency,
                    "stock": product.stock,
                    "rating": product.rating,
                    "features": product.features,
                    "use_cases": product.use_cases,
                    "warranty_months": product.warranty_months,
                    "specifications": product.specifications,
                }
            )
        return comparison
