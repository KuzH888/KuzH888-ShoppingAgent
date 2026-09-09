"""Product catalogue loading and validation helpers."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from src.models import Category, ProductCatalog


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CATALOG_PATH = PROJECT_ROOT / "data" / "products.json"
EXPECTED_PRODUCTS_PER_CATEGORY = 8


def load_catalog(path: Path | None = None) -> ProductCatalog:
    """Load the local product catalogue and enforce the approved MVP scope."""
    catalog_path = path or DEFAULT_CATALOG_PATH
    catalog = ProductCatalog.model_validate_json(catalog_path.read_text(encoding="utf-8"))

    counts = Counter(product.category for product in catalog.products)
    expected_categories = set(Category)
    if set(counts) != expected_categories:
        raise ValueError("The catalogue must contain all three approved categories")

    invalid_counts = {
        category.value: counts[category]
        for category in expected_categories
        if counts[category] != EXPECTED_PRODUCTS_PER_CATEGORY
    }
    if invalid_counts:
        raise ValueError(
            "Each category must contain exactly "
            f"{EXPECTED_PRODUCTS_PER_CATEGORY} products: {invalid_counts}"
        )

    return catalog


def main() -> None:
    """Validate the default catalogue and print a concise summary."""
    catalog = load_catalog()
    counts = Counter(product.category.value for product in catalog.products)
    print(f"Store: {catalog.store_name}")
    print(f"Products: {len(catalog.products)}")
    for category, count in sorted(counts.items()):
        print(f"- {category}: {count}")


if __name__ == "__main__":
    main()


def catalog_summary(catalog: ProductCatalog) -> dict[str, object]:
    """Return a deterministic, display-safe catalogue summary."""
    counts = Counter(product.category.value for product in catalog.products)
    return {
        "store_name": catalog.store_name,
        "version": catalog.version,
        "currency": catalog.currency,
        "product_count": len(catalog.products),
        "category_counts": dict(sorted(counts.items())),
        "in_stock_count": sum(product.stock > 0 for product in catalog.products),
    }
