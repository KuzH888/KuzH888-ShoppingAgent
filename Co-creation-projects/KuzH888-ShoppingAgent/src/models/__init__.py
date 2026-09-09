"""Data models for the shopping assistant."""

from .conversation import AssistantReply, ConversationState
from .product import Category, LocalizedText, Product, ProductCatalog
from .recommendation import (
    CustomerNeed,
    NearMatch,
    RecommendationResult,
    ScoredProduct,
)

__all__ = [
    "AssistantReply",
    "Category",
    "ConversationState",
    "CustomerNeed",
    "LocalizedText",
    "NearMatch",
    "Product",
    "ProductCatalog",
    "RecommendationResult",
    "ScoredProduct",
]
