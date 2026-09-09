"""Integration tests for the public FastAPI endpoints."""

from fastapi.testclient import TestClient

from src.api.app import app


client = TestClient(app)


def test_health_is_ready_and_does_not_expose_secrets():
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["simulation_mode"] is True
    assert "api_key" not in data


def test_model_list_is_available_for_frontend_selection():
    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.json()
    ids = [model["id"] for model in data["models"]]
    assert data["default_model"] in ids
    assert len(ids) == 3


def test_products_can_be_listed_and_filtered():
    all_products = client.get("/api/products")
    filtered = client.get("/api/products", params={"category": "home_office"})

    assert all_products.status_code == 200
    assert all_products.json()["total"] == 24
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 8
    assert all(
        product["category"] == "home_office"
        for product in filtered.json()["products"]
    )


def test_product_details_and_comparison_endpoints():
    details = client.get("/api/products/dig-001")
    comparison = client.post(
        "/api/products/compare",
        json={"product_ids": ["DIG-001", "DIG-003"], "language": "zh"},
    )

    assert details.status_code == 200
    assert details.json()["id"] == "DIG-001"
    assert comparison.status_code == 200
    assert [item["product_id"] for item in comparison.json()["products"]] == [
        "DIG-001",
        "DIG-003",
    ]


def test_policy_endpoints_return_validated_bilingual_content():
    policies = client.get("/api/policies")
    returns = client.get("/api/policies/returns")

    assert policies.status_code == 200
    assert len(policies.json()["policies"]) == 4
    assert returns.status_code == 200
    assert returns.json()["title"]["zh"] == "退换货政策"


def test_chat_preserves_session_context_in_simulation_mode():
    session_id = "api-follow-up"
    first = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "message": "I want headphones.",
            "model_id": "gpt-5.6-luna",
        },
    )
    second = client.post(
        "/api/chat",
        json={
            "session_id": session_id,
            "message": "For commuting, under AUD 100, with noise cancellation and lightweight.",
            "model_id": "gpt-5.6-luna",
        },
    )

    assert first.status_code == 200
    assert first.json()["result"]["type"] == "clarification"
    assert second.status_code == 200
    data = second.json()
    assert data["mode"] == "simulation"
    assert data["result"]["type"] == "recommendation"
    assert data["result"]["recommendations"][0]["product_id"] == "DIG-001"


def test_invalid_model_is_rejected():
    response = client.post(
        "/api/chat",
        json={
            "session_id": "invalid-model",
            "message": "I need headphones for commuting under AUD 100.",
            "model_id": "not-an-enabled-model",
        },
    )

    assert response.status_code == 400
    assert "Unsupported model" in response.json()["detail"]


def test_session_can_be_reset():
    session_id = "reset-api-session"
    client.post(
        "/api/chat",
        json={"session_id": session_id, "message": "I want headphones."},
    )
    response = client.delete(f"/api/sessions/{session_id}")

    assert response.status_code == 200
    assert response.json() == {"session_id": session_id, "reset": True}
