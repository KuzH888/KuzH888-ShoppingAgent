"""Tests for clarification, session memory and grounded reply formatting."""

import pytest

from src.agents import ShoppingAssistant, create_live_agent
from src.utils.config import ConfigurationError


def test_complete_chinese_request_returns_structured_recommendation():
    assistant = ShoppingAssistant()
    reply = assistant.chat(
        "我需要100澳元以内、适合通勤的耳机，降噪很重要，而且希望轻便。",
        session_id="zh-complete",
    )

    assert reply.type == "recommendation"
    assert reply.language == "zh"
    assert reply.recommendations[0].product_id == "DIG-001"
    assert "首选" in reply.message
    assert "DIG-001" in reply.message


def test_two_clarifying_questions_then_uses_session_context():
    assistant = ShoppingAssistant()
    first = assistant.chat("I want headphones.", session_id="en-follow-up")
    second = assistant.chat(
        "For commuting, under AUD 100, with noise cancellation and lightweight.",
        session_id="en-follow-up",
    )

    assert first.type == "clarification"
    assert len(first.questions) == 2
    assert second.type == "recommendation"
    assert second.recommendations[0].product_id == "DIG-001"
    assert second.message.startswith("Top pick:")
    assert assistant.get_state("en-follow-up").questions_asked == 2


def test_clarification_limit_is_two_questions():
    assistant = ShoppingAssistant()
    first = assistant.chat("请推荐商品", session_id="limit")
    second = assistant.chat("我还没想好", session_id="limit")

    assert len(first.questions) == 2
    assert second.type == "insufficient_information"
    assert not second.questions
    assert "信息仍不足" in second.message
    assert assistant.get_state("limit").questions_asked == 2


def test_customer_can_explicitly_decline_a_budget():
    assistant = ShoppingAssistant()
    reply = assistant.chat(
        "想买适合学习的护眼台灯，预算不限。",
        session_id="no-budget",
    )

    assert reply.type == "recommendation"
    assert reply.recommendations[0].product_id == "HOM-001"


def test_no_match_is_explicitly_labelled():
    assistant = ShoppingAssistant()
    reply = assistant.chat(
        "我必须买50澳元以内、适合通勤并带主动降噪的耳机。",
        session_id="no-match",
    )

    assert reply.type == "no_match"
    assert not reply.recommendations
    assert reply.alternatives
    assert "不是精确匹配" in reply.message


def test_reset_session_removes_previous_context():
    assistant = ShoppingAssistant()
    assistant.chat("I want headphones.", session_id="reset-me")
    assistant.reset_session("reset-me")

    assert assistant.get_state("reset-me").user_messages == []


def test_consecutive_duplicate_message_is_not_stored_twice():
    assistant = ShoppingAssistant()
    message = "我需要100澳元以内、适合通勤、轻便且降噪的耳机。"

    assistant.chat(message, session_id="duplicate")
    assistant.chat(message, session_id="duplicate")

    state = assistant.get_state("duplicate")
    assert state.user_messages == [message]


def test_product_detail_intent_uses_catalogue_facts_without_session_pollution():
    assistant = ShoppingAssistant()
    reply = assistant.chat("请介绍 DIG-001", session_id="details")

    assert reply.type == "product_details"
    assert reply.facts["product"]["id"] == "DIG-001"
    assert "AUD 89.90" in reply.message
    assert assistant.get_state("details").user_messages == []


def test_comparison_and_policy_intents_are_supported_in_simulation_mode():
    assistant = ShoppingAssistant()
    comparison = assistant.chat("比较 DIG-001 和 DIG-003", session_id="direct")
    policy = assistant.chat("请告诉我退货政策", session_id="direct")

    assert comparison.type == "comparison"
    assert len(comparison.facts["products"]) == 2
    assert "DIG-003" in comparison.message
    assert policy.type == "policy"
    assert policy.facts["policy"]["id"] == "returns"
    assert "30 天" in policy.message


def test_live_agent_stays_disabled_in_simulation_mode():
    with pytest.raises(ConfigurationError, match="APP_SIMULATION_MODE=true"):
        create_live_agent()
