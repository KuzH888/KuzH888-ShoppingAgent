"""Bilingual, catalogue-grounded response formatting."""

from __future__ import annotations

from src.models import CustomerNeed, NearMatch, Product, ScoredProduct, StorePolicy


LABELS = {
    "zh": {
        "active_noise_cancellation": "主动降噪",
        "lightweight": "轻便",
        "ergonomic": "人体工学",
        "wrist_rest": "腕托",
        "fast_charging": "快速充电",
        "multi_port": "多端口",
        "eye_care": "护眼",
        "foldable": "可折叠",
        "portable": "便携",
        "insulated": "保温",
        "leakproof": "防漏",
        "water_resistant": "防泼水",
        "laptop_compartment": "笔记本隔层",
        "neck_support": "颈部支撑",
        "rechargeable": "可充电",
        "commuting": "通勤",
        "study": "学习",
        "travel": "旅行",
        "hiking": "徒步",
        "long_typing": "长时间打字",
        "multiple_devices": "多设备使用",
        "air_travel": "乘机旅行",
        "summer": "夏季使用",
    },
    "en": {},
}


def _label(value: str, language: str) -> str:
    if language == "zh":
        return LABELS["zh"].get(value, value.replace("_", " "))
    return value.replace("_", " ")


def _matched_text(item: ScoredProduct, language: str) -> str:
    labels = [_label(value, language) for value in item.matched_requirements]
    if labels:
        return "、".join(labels) if language == "zh" else ", ".join(labels)
    return "综合评分、价格与口碑" if language == "zh" else "overall score, price and reviews"


def _tradeoff_text(item: ScoredProduct, language: str) -> str:
    if not item.tradeoffs:
        return "未发现明显偏好取舍" if language == "zh" else "no notable preference trade-offs"
    values = [_label(value.split(":", 1)[-1], language) for value in item.tradeoffs]
    return "、".join(values) if language == "zh" else ", ".join(values)


def format_recommendations(
    need: CustomerNeed,
    recommendations: list[ScoredProduct],
) -> str:
    """Render the approved primary-plus-alternatives reply layout."""
    if not recommendations:
        raise ValueError("At least one recommendation is required")

    primary = recommendations[0]
    if need.language == "zh":
        lines = [
            f"首选：{primary.name}（{primary.product_id}）",
            f"价格：{primary.currency} {primary.price:.2f}；匹配分：{primary.score:.2f}/100",
            f"推荐理由：符合{_matched_text(primary, 'zh')}。",
            f"主要取舍：{_tradeoff_text(primary, 'zh')}。",
        ]
        for index, item in enumerate(recommendations[1:], start=1):
            lines.extend(
                [
                    "",
                    f"备选 {index}：{item.name}（{item.product_id}）",
                    f"价格：{item.currency} {item.price:.2f}；匹配分：{item.score:.2f}/100",
                    f"适合点：{_matched_text(item, 'zh')}；取舍：{_tradeoff_text(item, 'zh')}。",
                ]
            )
        return "\n".join(lines)

    lines = [
        f"Top pick: {primary.name} ({primary.product_id})",
        f"Price: {primary.currency} {primary.price:.2f}; match score: {primary.score:.2f}/100",
        f"Why it fits: {_matched_text(primary, 'en')}.",
        f"Main trade-off: {_tradeoff_text(primary, 'en')}.",
    ]
    for index, item in enumerate(recommendations[1:], start=1):
        lines.extend(
            [
                "",
                f"Alternative {index}: {item.name} ({item.product_id})",
                f"Price: {item.currency} {item.price:.2f}; match score: {item.score:.2f}/100",
                f"Good for: {_matched_text(item, 'en')}; trade-off: {_tradeoff_text(item, 'en')}.",
            ]
        )
    return "\n".join(lines)


def _violation_text(violation: str, language: str) -> str:
    values = {
        "zh": {
            "out_of_stock": "暂时缺货",
            "wrong_product_type": "商品类型不符",
            "over_budget": "超过预算",
        },
        "en": {
            "out_of_stock": "out of stock",
            "wrong_product_type": "wrong product type",
            "over_budget": "over budget",
        },
    }
    if violation.startswith("missing_feature:"):
        feature = _label(violation.split(":", 1)[1], language)
        return f"缺少{feature}" if language == "zh" else f"missing {feature}"
    if violation.startswith("excluded_feature:"):
        feature = _label(violation.split(":", 1)[1], language)
        return f"包含已排除的{feature}" if language == "zh" else f"includes excluded {feature}"
    return values[language].get(violation, _label(violation, language))


def format_near_matches(need: CustomerNeed, alternatives: list[NearMatch]) -> str:
    """Clearly label fallback products and every violated constraint."""
    if need.language == "zh":
        lines = ["没有商品满足全部硬性条件。以下仅为近似备选，不是精确匹配："]
        for index, item in enumerate(alternatives, start=1):
            reasons = "、".join(_violation_text(value, "zh") for value in item.violations)
            lines.append(
                f"{index}. {item.name}（{item.product_id}），{item.currency} {item.price:.2f}；不符合：{reasons}。"
            )
        return "\n".join(lines)

    lines = ["No product meets every hard constraint. These are near matches, not exact matches:"]
    for index, item in enumerate(alternatives, start=1):
        reasons = ", ".join(_violation_text(value, "en") for value in item.violations)
        lines.append(
            f"{index}. {item.name} ({item.product_id}), {item.currency} {item.price:.2f}; does not meet: {reasons}."
        )
    return "\n".join(lines)


def format_product_details(product: Product, language: str) -> str:
    """Render one catalogue product without adding unsupported claims."""
    name = product.name.zh if language == "zh" else product.name.en
    description = product.description.zh if language == "zh" else product.description.en
    features = [_label(value, language) for value in product.features]
    use_cases = [_label(value, language) for value in product.use_cases]
    specs = ", ".join(f"{key}: {value}" for key, value in product.specifications.items())
    if language == "zh":
        stock = f"现货 {product.stock} 件" if product.stock else "暂时缺货"
        return "\n".join(
            [
                f"{name}（{product.id}）",
                description,
                f"价格：{product.currency} {product.price:.2f}；库存：{stock}",
                f"评分：{product.rating:.1f}/5（{product.review_count} 条评价）",
                f"主要功能：{'、'.join(features)}",
                f"适用场景：{'、'.join(use_cases)}",
                f"规格：{specs}",
                f"模拟保修期：{product.warranty_months} 个月。",
            ]
        )
    stock = f"{product.stock} in stock" if product.stock else "out of stock"
    return "\n".join(
        [
            f"{name} ({product.id})",
            description,
            f"Price: {product.currency} {product.price:.2f}; stock: {stock}",
            f"Rating: {product.rating:.1f}/5 ({product.review_count} reviews)",
            f"Key features: {', '.join(features)}",
            f"Use cases: {', '.join(use_cases)}",
            f"Specifications: {specs}",
            f"Simulated warranty: {product.warranty_months} months.",
        ]
    )


def format_comparison(products: list[dict], language: str) -> str:
    """Render a concise factual comparison for chat."""
    if language == "zh":
        lines = ["商品对比："]
        for product in products:
            features = "、".join(_label(value, "zh") for value in product["features"][:4])
            lines.append(
                f"- {product['name']}（{product['product_id']}）："
                f"{product['currency']} {product['price']:.2f}，评分 {product['rating']:.1f}/5，"
                f"库存 {product['stock']}，保修 {product['warranty_months']} 个月；主要功能：{features}。"
            )
        lines.append("你可以结合预算、主要功能和保修期选择；以上数据均来自本地商品目录。")
        return "\n".join(lines)
    lines = ["Product comparison:"]
    for product in products:
        features = ", ".join(_label(value, "en") for value in product["features"][:4])
        lines.append(
            f"- {product['name']} ({product['product_id']}): "
            f"{product['currency']} {product['price']:.2f}, rating {product['rating']:.1f}/5, "
            f"stock {product['stock']}, {product['warranty_months']}-month warranty; "
            f"key features: {features}."
        )
    lines.append("Choose based on budget, key features and warranty. All facts come from the local catalogue.")
    return "\n".join(lines)


def format_policy(policy: StorePolicy, language: str) -> str:
    """Render one bilingual store policy."""
    title = policy.title.zh if language == "zh" else policy.title.en
    summary = policy.summary.zh if language == "zh" else policy.summary.en
    details = [item.zh if language == "zh" else item.en for item in policy.details]
    return "\n".join([title, summary, *(f"- {detail}" for detail in details)])
