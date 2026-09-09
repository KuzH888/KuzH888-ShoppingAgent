"""Business services for KuzH888-ShoppingAgent."""

from .need_parser import parse_customer_need
from .recommendation import RecommendationEngine
from .response_formatter import format_near_matches, format_recommendations

__all__ = [
    "RecommendationEngine",
    "format_near_matches",
    "format_recommendations",
    "parse_customer_need",
]
