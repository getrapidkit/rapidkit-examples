"""Ecommerce API integration tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_product_cart_checkout_flow() -> None:
    product_payload = {
        "sku": "SKU-100",
        "name": "Wireless Keyboard",
        "price": "79.99",
        "currency": "usd",
        "stock": 5,
    }

    create_product = client.post("/api/v1/ecommerce/products", json=product_payload)
    assert create_product.status_code == 201
    product = create_product.json()
    assert product["sku"] == "SKU-100"
    assert product["currency"] == "USD"

    add_to_cart = client.post(
        "/api/v1/ecommerce/cart/items",
        json={"product_id": product["id"], "quantity": 2},
    )
    assert add_to_cart.status_code == 200
    cart = add_to_cart.json()
    assert cart["item_count"] == 2
    assert cart["subtotal"] == "159.98"

    checkout = client.post(
        "/api/v1/ecommerce/checkout",
        json={"customer_email": "buyer@example.com"},
    )
    assert checkout.status_code == 201
    order = checkout.json()
    assert order["status"] == "confirmed"
    assert order["total"] == "159.98"

    order_fetch = client.get(f"/api/v1/ecommerce/orders/{order['id']}")
    assert order_fetch.status_code == 200


def test_reject_insufficient_stock() -> None:
    create_product = client.post(
        "/api/v1/ecommerce/products",
        json={
            "sku": "SKU-LOW",
            "name": "Limited Item",
            "price": "10.00",
            "currency": "USD",
            "stock": 1,
        },
    )
    assert create_product.status_code == 201
    product_id = create_product.json()["id"]

    over_request = client.post(
        "/api/v1/ecommerce/cart/items",
        json={"product_id": product_id, "quantity": 2},
    )
    assert over_request.status_code == 400
    assert over_request.json()["detail"] == "Insufficient stock"


def test_seed_and_search_products() -> None:
    seeded = client.post("/api/v1/ecommerce/products/seed")
    assert seeded.status_code == 201

    search_by_term = client.get("/api/v1/ecommerce/products/search", params={"q": "mouse"})
    assert search_by_term.status_code == 200
    assert any("Mouse" in product["name"] for product in search_by_term.json())

    search_by_price = client.get(
        "/api/v1/ecommerce/products/search",
        params={"min_price": "50", "max_price": "120", "in_stock": "true"},
    )
    assert search_by_price.status_code == 200
    for product in search_by_price.json():
        assert float(product["price"]) >= 50
        assert float(product["price"]) <= 120


def test_payment_intent_and_webhook_flow() -> None:
    product = client.post(
        "/api/v1/ecommerce/products",
        json={
            "sku": "SKU-PAY-1",
            "name": "Checkout Item",
            "price": "25.00",
            "currency": "USD",
            "stock": 4,
        },
    ).json()

    add_to_cart = client.post(
        "/api/v1/ecommerce/cart/items",
        json={"product_id": product["id"], "quantity": 1},
    )
    assert add_to_cart.status_code == 200

    checkout = client.post(
        "/api/v1/ecommerce/checkout",
        json={"customer_email": "pay@example.com"},
    )
    assert checkout.status_code == 201
    order = checkout.json()
    assert order["status"] == "confirmed"

    create_intent = client.post(
        "/api/v1/ecommerce/payments/intents",
        json={"order_id": order["id"], "provider": "mockpay"},
    )
    assert create_intent.status_code == 201
    intent = create_intent.json()
    assert intent["status"] == "requires_confirmation"

    confirm_intent = client.post(
        f"/api/v1/ecommerce/payments/intents/{intent['id']}/confirm",
        json={"gateway_reference": "gw-test-001"},
    )
    assert confirm_intent.status_code == 200
    assert confirm_intent.json()["status"] == "succeeded"

    order_after_confirm = client.get(f"/api/v1/ecommerce/orders/{order['id']}")
    assert order_after_confirm.status_code == 200
    assert order_after_confirm.json()["status"] == "paid"

    webhook = client.post(
        "/api/v1/ecommerce/webhooks/payments",
        json={
            "event_type": "payment.failed",
            "payment_intent_id": intent["id"],
            "order_id": order["id"],
            "status": "failed",
        },
    )
    assert webhook.status_code == 202
    assert webhook.json()["order_status"] == "payment_failed"
