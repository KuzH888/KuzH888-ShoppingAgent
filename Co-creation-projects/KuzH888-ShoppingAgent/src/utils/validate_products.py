"""Command-line validation for data/products.json."""

from __future__ import annotations

import json

from src.utils.catalog import catalog_summary, load_catalog


def main() -> None:
    catalog = load_catalog()
    print(json.dumps(catalog_summary(catalog), ensure_ascii=False, indent=2))
    print("Product catalogue validation passed.")


if __name__ == "__main__":
    main()
