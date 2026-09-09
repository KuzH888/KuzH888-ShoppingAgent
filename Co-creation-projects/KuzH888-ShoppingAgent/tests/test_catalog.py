"""Tests for the approved 24-product KuzMall catalogue."""

from collections import Counter

from src.models import Category
from src.utils.catalog import EXPECTED_PRODUCTS_PER_CATEGORY, load_catalog


def test_catalog_has_approved_shape():
    catalog = load_catalog()
    counts = Counter(product.category for product in catalog.products)

    assert catalog.store_name == "KuzMall"
    assert catalog.currency == "AUD"
    assert len(catalog.products) == 24
    assert set(counts) == set(Category)
    assert all(count == EXPECTED_PRODUCTS_PER_CATEGORY for count in counts.values())


def test_product_identifiers_are_unique():
    catalog = load_catalog()
    ids = [product.id for product in catalog.products]
    skus = [product.sku for product in catalog.products]

    assert len(ids) == len(set(ids))
    assert len(skus) == len(set(skus))
