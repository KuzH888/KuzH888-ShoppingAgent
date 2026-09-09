"""Small bilingual rule parser used before live LLM integration."""

from __future__ import annotations

import re

from src.models import CustomerNeed


SUBCATEGORY_ALIASES = {
    "headphones": ("耳机", "headphone", "headphones", "earbud", "earbuds"),
    "keyboard": ("键盘", "keyboard"),
    "power_bank": ("移动电源", "充电宝", "power bank"),
    "charger": ("充电器", "charger"),
    "desk_lamp": ("台灯", "阅读灯", "desk lamp", "reading light"),
    "laptop_stand": ("笔记本支架", "电脑支架", "laptop stand"),
    "drinkware": ("水杯", "保温杯", "水瓶", "mug", "bottle"),
    "desk_organisation": ("桌面收纳", "收纳套装", "desk organiser", "desk organizer"),
    "cable_management": ("理线", "线材收纳", "cable management", "cable box"),
    "desk_fan": ("桌面风扇", "desk fan"),
    "backpack": ("背包", "backpack"),
    "travel_pillow": ("旅行枕", "travel pillow"),
    "portable_fan": ("便携风扇", "手持风扇", "portable fan", "handheld fan"),
    "packing_organiser": ("旅行收纳", "packing cube", "packing cubes"),
    "luggage_accessory": ("行李牌", "luggage tag"),
}

USE_CASE_ALIASES = {
    "commuting": ("通勤", "commute", "commuting"),
    "study": ("学习", "自习", "study", "studying"),
    "travel": ("旅行", "旅游", "出差", "travel", "trip"),
    "home_office": ("居家办公", "在家办公", "home office", "working from home"),
    "exercise": ("运动", "健身", "exercise", "gym"),
    "calls": ("通话", "会议", "calls", "meetings"),
    "music": ("音乐", "music"),
    "reading": ("阅读", "reading"),
    "summer": ("夏天", "夏季", "炎热", "summer", "hot weather"),
    "hiking": ("徒步", "远足", "hiking"),
    "long_typing": ("长时间打字", "大量打字", "long typing", "typing all day"),
    "multiple_devices": ("多设备", "多个设备", "multiple devices"),
    "air_travel": ("乘飞机", "飞机旅行", "air travel", "flight"),
    "business_travel": ("商务旅行", "商务出差", "business travel"),
}

FEATURE_ALIASES = {
    "active_noise_cancellation": ("主动降噪", "降噪", "anc", "noise cancellation", "noise cancelling"),
    "lightweight": ("轻便", "轻量", "lightweight", "light weight"),
    "bluetooth": ("蓝牙", "bluetooth"),
    "built_in_microphone": ("麦克风", "话筒", "microphone", "mic"),
    "water_resistant": ("防泼水", "防水", "water resistant", "water-resistant"),
    "compact": ("小巧", "紧凑", "compact"),
    "quiet_keys": ("静音按键", "安静按键", "quiet keys", "quiet keyboard"),
    "multi_device": ("多设备连接", "multi-device", "multi device"),
    "ergonomic": ("人体工学", "ergonomic"),
    "wrist_rest": ("掌托", "腕托", "wrist rest"),
    "fast_charging": ("快速充电", "快充", "fast charging", "fast-charging"),
    "high_capacity": ("大容量", "high capacity", "high-capacity"),
    "multi_port": ("多接口", "多端口", "multi port", "multi-port"),
    "eye_care": ("护眼", "eye care", "eye-care"),
    "height_adjustable": ("高度可调", "可调高度", "height adjustable", "adjustable height"),
    "foldable": ("折叠", "foldable", "folding"),
    "portable": ("便携", "portable"),
    "insulated": ("保温", "insulated"),
    "leakproof": ("防漏", "不漏", "leakproof", "leak-proof"),
    "laptop_compartment": ("笔记本隔层", "电脑隔层", "laptop compartment", "laptop sleeve"),
    "neck_support": ("颈部支撑", "护颈", "neck support"),
    "rechargeable": ("可充电", "充电式", "rechargeable"),
}

COLOR_ALIASES = {
    "black": ("黑色", "black"),
    "white": ("白色", "white"),
    "navy": ("深蓝", "海军蓝", "navy"),
    "blue": ("蓝色", "blue"),
    "grey": ("灰色", "grey", "gray"),
    "silver": ("银色", "silver"),
    "sage": ("鼠尾草绿", "sage"),
}

MUST_MARKERS = ("必须", "需要", "要有", "带有", "很重要", "重要", "must", "need", "required", "important", "with")
EXCLUDE_MARKERS = ("不要", "不想要", "避免", "排除", "without", "no ", "avoid", "exclude")


def _language(text: str) -> str:
    return "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en"


def _term_present(text: str, term: str) -> bool:
    """Match Latin aliases as complete words while keeping CJK substring matching."""
    if re.search(r"[a-z0-9]", term, flags=re.IGNORECASE):
        return re.search(
            rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])",
            text,
            flags=re.IGNORECASE,
        ) is not None
    return term in text


def _matches(text: str, aliases: dict[str, tuple[str, ...]]) -> list[str]:
    lowered = text.lower()
    return [key for key, terms in aliases.items() if any(_term_present(lowered, term) for term in terms)]


def _near_marker(text: str, term: str, markers: tuple[str, ...], radius: int = 24) -> bool:
    lowered = text.lower()
    start = lowered.find(term)
    if start < 0:
        return False
    window = lowered[max(0, start - radius) : start + len(term) + radius]
    return any(marker in window for marker in markers)


def _split_feature_intent(text: str) -> tuple[list[str], list[str], list[str]]:
    lowered = text.lower()
    must_have: list[str] = []
    preferences: list[str] = []
    excluded: list[str] = []
    for feature, aliases in FEATURE_ALIASES.items():
        present_terms = [term for term in aliases if _term_present(lowered, term)]
        if not present_terms:
            continue
        if any(_near_marker(lowered, term, EXCLUDE_MARKERS) for term in present_terms):
            excluded.append(feature)
        elif any(_near_marker(lowered, term, MUST_MARKERS) for term in present_terms):
            must_have.append(feature)
        else:
            preferences.append(feature)
    return must_have, preferences, excluded


def _parse_budget(text: str) -> float | None:
    patterns = (
        r"(?:预算|不超过|以内|低于|最多)\s*(?:是|为|约|大约)?\s*(?:aud|a\$|\$)?\s*(\d+(?:\.\d+)?)",
        r"(?:aud|a\$|\$)\s*(\d+(?:\.\d+)?)\s*(?:以内|以下|以下预算)?",
        r"(?:budget(?: is| of)?|under|below|up to|max(?:imum)?)\s*(?:aud|a\$|\$)?\s*(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*(?:澳元|aud)\s*(?:以内|以下|预算)",
    )
    lowered = text.lower()
    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return float(match.group(1))
    return None


def _parse_colors(text: str) -> tuple[list[str], list[str]]:
    lowered = text.lower()
    preferred: list[str] = []
    excluded: list[str] = []
    for color, aliases in COLOR_ALIASES.items():
        terms = [term for term in aliases if _term_present(lowered, term)]
        if not terms:
            continue
        if any(_near_marker(lowered, term, EXCLUDE_MARKERS) for term in terms):
            excluded.append(color)
        else:
            preferred.append(color)
    return preferred, excluded


def parse_customer_need(query: str) -> CustomerNeed:
    """Convert a simple Chinese or English shopping query into fixed fields."""
    cleaned = query.strip()
    if not cleaned:
        raise ValueError("Customer query cannot be empty")

    must_have, preferences, excluded_features = _split_feature_intent(cleaned)
    preferred_colors, excluded_colors = _parse_colors(cleaned)
    return CustomerNeed(
        original_query=cleaned,
        language=_language(cleaned),
        target_subcategories=_matches(cleaned, SUBCATEGORY_ALIASES),
        budget_max=_parse_budget(cleaned),
        use_cases=_matches(cleaned, USE_CASE_ALIASES),
        must_have=must_have,
        preferences=preferences,
        excluded_features=excluded_features,
        preferred_colors=preferred_colors,
        excluded_colors=excluded_colors,
    )
