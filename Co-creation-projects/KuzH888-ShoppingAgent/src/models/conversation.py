"""Conversation models shared by the notebook and future web API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from .recommendation import CustomerNeed, NearMatch, ScoredProduct


class ConversationState(BaseModel):
    """Short-lived state for one browser chat session."""

    model_config = ConfigDict(extra="forbid")

    user_messages: list[str] = Field(default_factory=list)
    questions_asked: int = Field(default=0, ge=0, le=2)
    budget_declined: bool = False


class AssistantReply(BaseModel):
    """Structured response returned by both simulation and web layers."""

    model_config = ConfigDict(extra="forbid")

    type: Literal[
        "clarification",
        "recommendation",
        "no_match",
        "product_details",
        "comparison",
        "policy",
        "insufficient_information",
        "error",
    ]
    language: Literal["zh", "en"]
    message: str
    need: CustomerNeed | None = None
    questions: list[str] = Field(default_factory=list)
    recommendations: list[ScoredProduct] = Field(default_factory=list)
    alternatives: list[NearMatch] = Field(default_factory=list)
    facts: dict[str, Any] = Field(default_factory=dict)
