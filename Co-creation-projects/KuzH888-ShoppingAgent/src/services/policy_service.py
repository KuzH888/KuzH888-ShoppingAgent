"""Deterministic lookup for the local bilingual store policies."""

from __future__ import annotations

from src.models import StorePolicies, StorePolicy
from src.utils.policies import load_policies


class PolicyService:
    def __init__(self, policies: StorePolicies | None = None):
        self.policies = policies or load_policies()
        self._by_id = {policy.id: policy for policy in self.policies.policies}

    def get(self, policy_id: str) -> StorePolicy:
        try:
            return self._by_id[policy_id.strip().lower()]
        except KeyError as exc:
            raise ValueError(f"Unknown policy ID: {policy_id}") from exc
