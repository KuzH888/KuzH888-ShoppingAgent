"""Safe runtime configuration and model allow-list handling."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = PROJECT_ROOT / ".env"
MODEL_CATALOG_PATH = PROJECT_ROOT / "config" / "models.json"


class ConfigurationError(ValueError):
    """Raised when application configuration is missing or invalid."""


@dataclass(frozen=True)
class RuntimeConfig:
    """Validated server-side LLM configuration."""

    provider: str
    model_id: str
    base_url: str
    api_key: str
    simulation_mode: bool

    def public_dict(self) -> dict[str, Any]:
        """Return configuration that is safe to expose to logs or a frontend."""
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "base_url": self.base_url,
            "api_key_configured": bool(self.api_key),
            "simulation_mode": self.simulation_mode,
        }


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def load_model_catalog() -> dict[str, Any]:
    """Load and validate the public model catalogue."""
    try:
        with MODEL_CATALOG_PATH.open(encoding="utf-8") as file:
            catalog = json.load(file)
    except FileNotFoundError as exc:
        raise ConfigurationError(
            f"Model catalogue not found: {MODEL_CATALOG_PATH}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError("config/models.json is not valid JSON") from exc

    models = catalog.get("models")
    default_model = catalog.get("default_model")
    if not isinstance(models, list) or not models:
        raise ConfigurationError("The model catalogue must contain a non-empty models list")

    enabled_ids = {
        model.get("id")
        for model in models
        if isinstance(model, dict) and model.get("enabled") is True
    }
    if default_model not in enabled_ids:
        raise ConfigurationError("The default model must be enabled in the model catalogue")

    return catalog


def list_public_models() -> list[dict[str, str]]:
    """Return enabled model metadata that is safe for a frontend dropdown."""
    catalog = load_model_catalog()
    public_models = []
    for model in catalog["models"]:
        if model.get("enabled") is True:
            public_models.append(
                {
                    "id": model["id"],
                    "label": model["label"],
                    "provider": model["provider"],
                    "description_zh": model.get("description_zh", ""),
                    "description_en": model.get("description_en", ""),
                }
            )
    return public_models


def validate_model_id(model_id: str) -> str:
    """Reject model IDs that are not enabled in the server-side allow-list."""
    allowed_ids = {model["id"] for model in list_public_models()}
    if model_id not in allowed_ids:
        raise ConfigurationError(f"Unsupported model: {model_id}")
    return model_id


def load_runtime_config(
    selected_model: str | None = None,
    *,
    require_api_key: bool = False,
) -> RuntimeConfig:
    """Load local settings and validate the selected model without exposing secrets."""
    load_dotenv(ENV_PATH)
    catalog = load_model_catalog()

    model_id = selected_model or os.getenv("LLM_MODEL_ID") or catalog["default_model"]
    validate_model_id(model_id)

    provider = os.getenv("LLM_PROVIDER", "openai").strip().lower()
    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").strip()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    simulation_mode = _as_bool(os.getenv("APP_SIMULATION_MODE"), default=True)

    if provider != "openai":
        raise ConfigurationError("The current model catalogue only enables OpenAI")
    if not base_url.startswith("https://"):
        raise ConfigurationError("LLM_BASE_URL must use HTTPS")
    if require_api_key and not api_key:
        raise ConfigurationError(
            "LLM_API_KEY is required when live API testing is enabled"
        )

    return RuntimeConfig(
        provider=provider,
        model_id=model_id,
        base_url=base_url,
        api_key=api_key,
        simulation_mode=simulation_mode,
    )
