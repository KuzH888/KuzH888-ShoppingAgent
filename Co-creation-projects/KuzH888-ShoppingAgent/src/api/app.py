"""FastAPI application exposing the shopping assistant as JSON endpoints."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.agents import ShoppingAssistant, create_live_agent
from src.models import Category, Product, StorePolicy
from src.services import PolicyService, RecommendationEngine
from src.utils.catalog import load_catalog
from src.utils.config import ConfigurationError, list_public_models, load_runtime_config

from .schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    ModelsResponse,
    PolicyListResponse,
    ProductComparisonRequest,
    ProductComparisonResponse,
    ProductListResponse,
    SessionResetResponse,
)


APP_VERSION = "0.5.0"
LOCAL_FRONTEND_ORIGINS = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app = FastAPI(
    title="KuzH888 ShoppingAgent API",
    description="Backend API for the KuzMall multilingual shopping assistant.",
    version=APP_VERSION,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=LOCAL_FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

catalog = load_catalog()
recommendation_engine = RecommendationEngine(catalog)
policy_service = PolicyService()
simulation_assistant = ShoppingAssistant()
live_agents: dict[tuple[str, str], object] = {}


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Return a secret-free readiness summary."""
    config = load_runtime_config()
    return HealthResponse(
        status="ok",
        service="KuzH888 ShoppingAgent API",
        version=APP_VERSION,
        simulation_mode=config.simulation_mode,
        api_key_configured=bool(config.api_key),
    )


@app.get("/api/models", response_model=ModelsResponse, tags=["configuration"])
def get_models() -> ModelsResponse:
    """Return the server-side model allow-list for a frontend dropdown."""
    config = load_runtime_config()
    return ModelsResponse(default_model=config.model_id, models=list_public_models())


@app.get("/api/products", response_model=ProductListResponse, tags=["catalogue"])
def get_products(
    category: Category | None = Query(default=None),
) -> ProductListResponse:
    """Return all products or one validated catalogue category."""
    products = catalog.products
    if category is not None:
        products = [product for product in products if product.category == category]
    return ProductListResponse(total=len(products), products=products)


@app.post(
    "/api/products/compare",
    response_model=ProductComparisonResponse,
    tags=["catalogue"],
)
def compare_products(request: ProductComparisonRequest) -> ProductComparisonResponse:
    """Return a factual side-by-side comparison for two or three products."""
    product_ids = [product_id.strip().upper() for product_id in request.product_ids]
    try:
        products = recommendation_engine.compare(product_ids, language=request.language)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProductComparisonResponse(products=products)


@app.get("/api/products/{product_id}", response_model=Product, tags=["catalogue"])
def get_product(product_id: str) -> Product:
    """Return the complete validated record for one product ID."""
    try:
        return recommendation_engine.get_product(product_id.strip().upper())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/policies", response_model=PolicyListResponse, tags=["policies"])
def get_policies() -> PolicyListResponse:
    """Return all fictional bilingual store policies."""
    return PolicyListResponse(policies=policy_service.policies.policies)


@app.get("/api/policies/{policy_id}", response_model=StorePolicy, tags=["policies"])
def get_policy(policy_id: str) -> StorePolicy:
    """Return one fictional store policy."""
    try:
        return policy_service.get(policy_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/chat", response_model=ChatResponse, tags=["assistant"])
def chat(request: ChatRequest) -> ChatResponse:
    """Chat locally in simulation mode or use the selected live model."""
    try:
        config = load_runtime_config(selected_model=request.model_id)
    except ConfigurationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if config.simulation_mode:
        reply = simulation_assistant.chat(
            request.message,
            session_id=request.session_id,
        )
        return ChatResponse(
            session_id=request.session_id,
            model_id=config.model_id,
            mode="simulation",
            message=reply.message,
            result=reply,
        )

    cache_key = (request.session_id, config.model_id)
    try:
        agent = live_agents.get(cache_key)
        if agent is None:
            agent = create_live_agent(selected_model=config.model_id)
            live_agents[cache_key] = agent
        message = agent.run(request.message)
    except ConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The selected LLM provider could not complete the request.",
        ) from exc

    return ChatResponse(
        session_id=request.session_id,
        model_id=config.model_id,
        mode="live",
        message=str(message),
    )


@app.delete(
    "/api/sessions/{session_id}",
    response_model=SessionResetResponse,
    tags=["assistant"],
)
def reset_session(session_id: str) -> SessionResetResponse:
    """Clear local and live in-memory state for one browser session."""
    simulation_assistant.reset_session(session_id)
    for cache_key in [key for key in live_agents if key[0] == session_id]:
        live_agents.pop(cache_key, None)
    return SessionResetResponse(session_id=session_id, reset=True)
