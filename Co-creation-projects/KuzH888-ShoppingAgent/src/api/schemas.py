"""Public request and response schemas for the FastAPI backend."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from src.models import AssistantReply, Product


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok"]
    service: str
    version: str
    simulation_mode: bool
    api_key_configured: bool


class ModelsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    default_model: str
    models: list[dict[str, str]]


class ProductListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total: int = Field(ge=0)
    products: list[Product]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    session_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1, max_length=2000)
    model_id: str | None = None


class ChatResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    model_id: str
    mode: Literal["simulation", "live"]
    message: str
    result: AssistantReply | None = None


class SessionResetResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    reset: Literal[True]
