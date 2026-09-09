"""Load the validated local KuzMall policy catalogue."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from src.models import StorePolicies


PROJECT_ROOT = Path(__file__).resolve().parents[2]
POLICIES_PATH = PROJECT_ROOT / "data" / "store_policies.json"


def load_policies(path: Path = POLICIES_PATH) -> StorePolicies:
    try:
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
        return StorePolicies.model_validate(payload)
    except FileNotFoundError as exc:
        raise ValueError(f"Policy data not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("Policy data is not valid JSON") from exc
    except ValidationError as exc:
        raise ValueError(f"Policy data validation failed: {exc}") from exc
