"""Validated product catalogue models."""

from __future__ import annotations

from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Category(str, Enum):
    """Product categories supported by the first KuzMall catalogue."""

    DIGITAL_ACCESSORIES = "digital_accessories"
    HOME_OFFICE = "home_office"
    TRAVEL_LIFESTYLE = "travel_lifestyle"


class LocalizedText(BaseModel):
    """Chinese and English text displayed by the storefront and assistant."""

    model_config = ConfigDict(extra="forbid")

    zh: str = Field(min_length=1)
    en: str = Field(min_length=1)


class Product(BaseModel):
    """One deterministic, locally stored catalogue product."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[A-Z]{3}-\d{3}$")
    sku: str = Field(pattern=r"^KUZ-[A-Z]{3}-\d{3}$")
    name: LocalizedText
    description: LocalizedText
    category: Category
    subcategory: str = Field(min_length=1)
    price: float = Field(gt=0)
    currency: Literal["AUD"] = "AUD"
    stock: int = Field(ge=0)
    rating: float = Field(ge=0, le=5)
    review_count: int = Field(ge=0)
    use_cases: list[str] = Field(min_length=1)
    features: list[str] = Field(min_length=1)
    colors: list[str] = Field(min_length=1)
    warranty_months: int = Field(ge=0)
    specifications: dict[str, Any]
    image_path: str = Field(min_length=1)

    @field_validator("use_cases", "features", "colors")
    @classmethod
    def values_must_be_unique(cls, values: list[str]) -> list[str]:
        if len(values) != len(set(values)):
            raise ValueError("List values must be unique")
        return values

    @field_validator("image_path")
    @classmethod
    def image_path_must_be_safe(cls, value: str) -> str:
        path = PurePosixPath(value)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("image_path must be a safe project-relative path")
        return value


class ProductCatalog(BaseModel):
    """Versioned KuzMall catalogue with cross-product validation."""

    model_config = ConfigDict(extra="forbid")

    version: str = Field(min_length=1)
    store_name: str = Field(min_length=1)
    currency: Literal["AUD"] = "AUD"
    products: list[Product] = Field(min_length=1)

    @model_validator(mode="after")
    def product_identifiers_must_be_unique(self) -> "ProductCatalog":
        ids = [product.id for product in self.products]
        skus = [product.sku for product in self.products]
        if len(ids) != len(set(ids)):
            raise ValueError("Product IDs must be unique")
        if len(skus) != len(set(skus)):
            raise ValueError("Product SKUs must be unique")
        return self
