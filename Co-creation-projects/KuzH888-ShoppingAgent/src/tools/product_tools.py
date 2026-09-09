"""HelloAgents-compatible tools backed by deterministic local product data."""

from __future__ import annotations

from hello_agents.tools import Tool, ToolParameter, ToolResponse

from src.services import RecommendationEngine, parse_customer_need
from src.utils.catalog import load_catalog


class SearchProductsTool(Tool):
    """Parse a bilingual query and return ranked catalogue recommendations."""

    def __init__(self, engine: RecommendationEngine | None = None):
        super().__init__(
            name="search_products",
            description=(
                "根据中文或英文购物需求过滤并排序 KuzMall 商品。"
                "返回精确匹配，或者明确标记不满足硬性条件的备选。"
            ),
        )
        self.engine = engine or RecommendationEngine(load_catalog())

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="query",
                type="string",
                description="包含品类、预算、场景、必备功能和偏好的购物需求",
                required=True,
            )
        ]

    def run(self, parameters: dict) -> ToolResponse:
        query = str(parameters.get("query", "")).strip()
        if not query:
            return ToolResponse.error(
                code="INVALID_QUERY",
                message="query cannot be empty",
            )
        try:
            need = parse_customer_need(query)
            result = self.engine.recommend(need)
        except (TypeError, ValueError) as exc:
            return ToolResponse.error(code="RECOMMENDATION_ERROR", message=str(exc))

        return ToolResponse.success(
            text=result.message,
            data=result.model_dump(mode="json"),
        )

class ProductDetailsTool(Tool):
    """Return factual details for one known product ID."""

    def __init__(self, engine: RecommendationEngine | None = None):
        super().__init__(
            name="get_product_details",
            description="根据商品 ID 获取商品数据库中的完整事实。",
        )
        self.engine = engine or RecommendationEngine(load_catalog())

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="product_id",
                type="string",
                description="商品 ID，例如 DIG-001",
                required=True,
            )
        ]

    def run(self, parameters: dict) -> ToolResponse:
        product_id = str(parameters.get("product_id", "")).strip().upper()
        try:
            product = self.engine.get_product(product_id)
        except ValueError as exc:
            return ToolResponse.error(code="PRODUCT_NOT_FOUND", message=str(exc))
        return ToolResponse.success(
            text=f"Product found: {product_id}",
            data=product.model_dump(mode="json"),
        )


class CompareProductsTool(Tool):
    """Compare two or three products without inventing attributes."""

    def __init__(self, engine: RecommendationEngine | None = None):
        super().__init__(
            name="compare_products",
            description="比较两到三件 KuzMall 商品的价格、评分、功能、场景和规格。",
        )
        self.engine = engine or RecommendationEngine(load_catalog())

    def get_parameters(self) -> list[ToolParameter]:
        return [
            ToolParameter(
                name="product_ids",
                type="array",
                description="需要比较的两个或三个商品 ID",
                required=True,
            ),
            ToolParameter(
                name="language",
                type="string",
                description="输出商品名称所使用的语言：zh 或 en",
                required=False,
                default="zh",
            ),
        ]

    def run(self, parameters: dict) -> ToolResponse:
        product_ids = parameters.get("product_ids", [])
        language = str(parameters.get("language", "zh")).lower()
        if language not in {"zh", "en"}:
            return ToolResponse.error(
                code="INVALID_LANGUAGE",
                message="language must be zh or en",
            )
        if not isinstance(product_ids, list):
            return ToolResponse.error(
                code="INVALID_PRODUCT_IDS",
                message="product_ids must be a list",
            )
        try:
            data = self.engine.compare(product_ids, language=language)
        except ValueError as exc:
            return ToolResponse.error(code="COMPARISON_ERROR", message=str(exc))
        return ToolResponse.success(
            text="商品比较数据已生成。" if language == "zh" else "Product comparison generated.",
            data={"products": data},
        )
