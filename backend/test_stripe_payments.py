"""Integration tests for Stripe payment endpoints."""

import uuid

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

import server


@pytest.fixture
def client():
    mongo_url = server.resolve_mongo_url()
    if mongo_url:
        server.client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000, connectTimeoutMS=10000)
        server.db = server.client[server.resolve_db_name()]

    with TestClient(server.app) as test_client:
        yield test_client

    if server.client is not None:
        server.client.close()


def _create_user_and_headers(client: TestClient):
    email = f"payments_{uuid.uuid4().hex[:10]}@example.com"
    response = client.post(
        "/api/auth/signup",
        json={
            "email": email,
            "password": "auditpass123",
            "first_name": "Payment",
            "last_name": "Audit"
        }
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    return email, {"Authorization": f"Bearer {payload['access_token']}"}


def _create_product(client: TestClient, headers: dict[str, str]):
    response = client.post(
        "/api/products",
        headers=headers,
        json={
            "title": f"Checkout Test Product {uuid.uuid4().hex[:6]}",
            "description": "Integration test product for Stripe checkout.",
            "product_type": "ebook",
            "price": 29.99,
            "tags": ["test", "payments"]
        }
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_create_checkout(client: TestClient):
    stripe_key = server.keys_manager.get_key("stripe_key")
    if not stripe_key:
        pytest.skip("Stripe API key is not configured")

    email, headers = _create_user_and_headers(client)
    product = _create_product(client, headers)

    response = client.post(
        "/api/payments/create-checkout",
        json={
            "product_id": product["id"],
            "customer_email": email,
            "quantity": 1
        }
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["payment_status"] == "pending"
    assert payload["session_id"]
    assert payload["checkout_url"].startswith("https://checkout.stripe.com/")


def test_product_payment_stats(client: TestClient):
    _, headers = _create_user_and_headers(client)
    product = _create_product(client, headers)

    response = client.get(f"/api/payments/{product['id']}/stats")

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["product_id"] == product["id"]
    assert payload["total_sales"] >= 0
    assert payload["total_revenue"] >= 0


def test_all_payment_stats(client: TestClient):
    response = client.get("/api/payments/all-stats")

    assert response.status_code == 200, response.text
    payload = response.json()
    for key in [
        "total_revenue",
        "total_sales",
        "products_with_sales",
        "average_order_value",
        "today_revenue",
        "today_sales"
    ]:
        assert key in payload


def test_webhook_requires_valid_configuration(client: TestClient):
    response = client.post("/api/payments/webhook", content=b"{}")

    assert response.status_code in {400, 500}, response.text
    payload = response.json()
    assert "detail" in payload
