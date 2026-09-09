"""Validated bilingual policies for the simulated KuzMall store."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .product import LocalizedText


class StorePolicy(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z_]+$")
    title: LocalizedText
    summary: LocalizedText
    details: list[LocalizedText] = Field(min_length=1)


class StorePolicies(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: str = Field(min_length=1)
    store_name: str = Field(min_length=1)
    policies: list[StorePolicy] = Field(min_length=1)

    @model_validator(mode="after")
    def identifiers_must_be_unique(self) -> "StorePolicies":
        identifiers = [policy.id for policy in self.policies]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("Policy IDs must be unique")
        return self
