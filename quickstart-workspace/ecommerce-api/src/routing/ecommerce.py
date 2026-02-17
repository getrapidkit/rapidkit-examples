"""Production-style ecommerce routes for catalog, cart, and checkout."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from threading import Lock
from typing import Dict, List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/ecommerce", tags=["ecommerce"])


class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=3, max_length=40)
    name: str = Field(..., min_length=2, max_length=120)
    price: Decimal = Field(..., gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    stock: int = Field(default=0, ge=0)


class Product(ProductCreate):
    id: str


class CartItemCreate(BaseModel):
    product_id: str
    quantity: int = Field(default=1, ge=1, le=100)


class CartItem(BaseModel):
    product_id: str
    sku: str
    name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class Cart(BaseModel):
    items: List[CartItem]
    item_count: int
    subtotal: Decimal
    currency: str


class CheckoutRequest(BaseModel):
    customer_email: str = Field(..., min_length=5, max_length=255)


class Order(BaseModel):
    id: str
    created_at: str
    customer_email: str
    items: List[CartItem]
    total: Decimal
    currency: str
    status: str


class PaymentIntentCreate(BaseModel):
    order_id: str
    provider: str = Field(default="mockpay", min_length=3, max_length=40)


class PaymentConfirmRequest(BaseModel):
    gateway_reference: str | None = Field(default=None, max_length=120)


class PaymentIntent(BaseModel):
    id: str
    order_id: str
    amount: Decimal
    currency: str
    provider: str
    status: str
    client_secret: str
    created_at: str
    gateway_reference: str | None = None


class PaymentWebhookEvent(BaseModel):
    event_type: str = Field(..., min_length=5, max_length=80)
    payment_intent_id: str
    order_id: str
    status: str = Field(..., min_length=2, max_length=40)
    signature: str | None = None


_PRODUCTS: Dict[str, Product] = {}
_CART_ITEMS: Dict[str, int] = {}
_ORDERS: Dict[str, Order] = {}
_PAYMENT_INTENTS: Dict[str, PaymentIntent] = {}
_WEBHOOK_EVENTS: List[PaymentWebhookEvent] = []
_LOCK = Lock()

_SEED_PRODUCTS: tuple[ProductCreate, ...] = (
    ProductCreate(
        sku="SKU-KB-001",
        name="Mechanical Keyboard",
        price=Decimal("99.90"),
        currency="USD",
        stock=20,
    ),
    ProductCreate(
        sku="SKU-MS-001",
        name="Ergonomic Mouse",
        price=Decimal("39.50"),
        currency="USD",
        stock=30,
    ),
    ProductCreate(
        sku="SKU-HD-001",
        name="USB-C Hub",
        price=Decimal("54.00"),
        currency="USD",
        stock=15,
    ),
)


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _normalize_currency(code: str) -> str:
    return code.strip().upper()


def _get_product_or_404(product_id: str) -> Product:
    product = _PRODUCTS.get(product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def _get_order_or_404(order_id: str) -> Order:
    order = _ORDERS.get(order_id)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def _build_cart() -> Cart:
    items: List[CartItem] = []
    subtotal = Decimal("0")
    currency = "USD"

    for product_id, quantity in _CART_ITEMS.items():
        product = _PRODUCTS.get(product_id)
        if product is None:
            continue
        currency = _normalize_currency(product.currency)
        line_total = _money(product.price * quantity)
        subtotal += line_total
        items.append(
            CartItem(
                product_id=product.id,
                sku=product.sku,
                name=product.name,
                quantity=quantity,
                unit_price=_money(product.price),
                line_total=line_total,
            )
        )

    return Cart(
        items=items,
        item_count=sum(item.quantity for item in items),
        subtotal=_money(subtotal),
        currency=currency,
    )


@router.get("/products", response_model=List[Product], summary="List products")
def list_products() -> List[Product]:
    return list(_PRODUCTS.values())


@router.get("/products/search", response_model=List[Product], summary="Search products")
def search_products(
    q: str = Query(default="", min_length=0, max_length=120),
    min_price: Decimal | None = Query(default=None, gt=0),
    max_price: Decimal | None = Query(default=None, gt=0),
    in_stock: bool | None = Query(default=None),
) -> List[Product]:
    term = q.strip().lower()
    products = list(_PRODUCTS.values())

    if term:
        products = [
            product
            for product in products
            if term in product.name.lower() or term in product.sku.lower()
        ]

    if min_price is not None:
        products = [product for product in products if product.price >= min_price]

    if max_price is not None:
        products = [product for product in products if product.price <= max_price]

    if in_stock is True:
        products = [product for product in products if product.stock > 0]
    elif in_stock is False:
        products = [product for product in products if product.stock == 0]

    return products


@router.post(
    "/products",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
)
def create_product(payload: ProductCreate) -> Product:
    product_id = f"prd_{uuid4().hex[:10]}"
    product = Product(
        id=product_id,
        sku=payload.sku.strip().upper(),
        name=payload.name.strip(),
        price=_money(payload.price),
        currency=_normalize_currency(payload.currency),
        stock=payload.stock,
    )
    with _LOCK:
        _PRODUCTS[product.id] = product
    return product


@router.post(
    "/products/seed",
    response_model=List[Product],
    status_code=status.HTTP_201_CREATED,
    summary="Seed sample catalog",
)
def seed_products() -> List[Product]:
    seeded: List[Product] = []
    with _LOCK:
        existing_skus = {product.sku for product in _PRODUCTS.values()}
        for item in _SEED_PRODUCTS:
            sku = item.sku.strip().upper()
            if sku in existing_skus:
                continue
            product_id = f"prd_{uuid4().hex[:10]}"
            product = Product(
                id=product_id,
                sku=sku,
                name=item.name,
                price=_money(item.price),
                currency=_normalize_currency(item.currency),
                stock=item.stock,
            )
            _PRODUCTS[product.id] = product
            existing_skus.add(sku)
            seeded.append(product)
    return seeded


@router.get("/products/{product_id}", response_model=Product, summary="Get product")
def get_product(product_id: str) -> Product:
    return _get_product_or_404(product_id)


@router.post(
    "/cart/items",
    response_model=Cart,
    status_code=status.HTTP_200_OK,
    summary="Add item to cart",
)
def add_item_to_cart(payload: CartItemCreate) -> Cart:
    with _LOCK:
        product = _get_product_or_404(payload.product_id)
        current_qty = _CART_ITEMS.get(product.id, 0)
        next_qty = current_qty + payload.quantity
        if next_qty > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock",
            )
        _CART_ITEMS[product.id] = next_qty
        return _build_cart()


@router.get("/cart", response_model=Cart, summary="Get active cart")
def get_cart() -> Cart:
    return _build_cart()


@router.delete("/cart", response_model=Cart, summary="Clear cart")
def clear_cart() -> Cart:
    with _LOCK:
        _CART_ITEMS.clear()
        return _build_cart()


@router.post(
    "/checkout",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    summary="Checkout cart and create order",
)
def checkout(payload: CheckoutRequest) -> Order:
    with _LOCK:
        cart = _build_cart()
        if not cart.items:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty")

        for item in cart.items:
            product = _get_product_or_404(item.product_id)
            if item.quantity > product.stock:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock for {product.sku}",
                )

        for item in cart.items:
            product = _get_product_or_404(item.product_id)
            _PRODUCTS[item.product_id] = product.model_copy(
                update={"stock": product.stock - item.quantity}
            )

        order = Order(
            id=f"ord_{uuid4().hex[:10]}",
            created_at=datetime.now(timezone.utc).isoformat(),
            customer_email=payload.customer_email.strip().lower(),
            items=cart.items,
            total=cart.subtotal,
            currency=cart.currency,
            status="confirmed",
        )
        _ORDERS[order.id] = order
        _CART_ITEMS.clear()
        return order


@router.get("/orders/{order_id}", response_model=Order, summary="Get order")
def get_order(order_id: str) -> Order:
    return _get_order_or_404(order_id)


@router.post(
    "/payments/intents",
    response_model=PaymentIntent,
    status_code=status.HTTP_201_CREATED,
    summary="Create mock payment intent",
)
def create_payment_intent(payload: PaymentIntentCreate) -> PaymentIntent:
    with _LOCK:
        order = _get_order_or_404(payload.order_id)
        if order.status == "paid":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Order already paid",
            )

        intent = PaymentIntent(
            id=f"pi_{uuid4().hex[:12]}",
            order_id=order.id,
            amount=order.total,
            currency=order.currency,
            provider=payload.provider.strip().lower(),
            status="requires_confirmation",
            client_secret=f"cs_{uuid4().hex}",
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        _PAYMENT_INTENTS[intent.id] = intent
        return intent


@router.post(
    "/payments/intents/{intent_id}/confirm",
    response_model=PaymentIntent,
    summary="Confirm mock payment intent",
)
def confirm_payment_intent(intent_id: str, payload: PaymentConfirmRequest) -> PaymentIntent:
    with _LOCK:
        intent = _PAYMENT_INTENTS.get(intent_id)
        if intent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment intent not found",
            )

        updated_intent = intent.model_copy(
            update={
                "status": "succeeded",
                "gateway_reference": payload.gateway_reference or f"gw_{uuid4().hex[:10]}",
            }
        )
        _PAYMENT_INTENTS[intent_id] = updated_intent

        order = _get_order_or_404(intent.order_id)
        _ORDERS[order.id] = order.model_copy(update={"status": "paid"})
        return updated_intent


@router.post(
    "/webhooks/payments",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Handle mock payment webhook",
)
def handle_payment_webhook(event: PaymentWebhookEvent) -> dict[str, object]:
    allowed_events = {"payment.succeeded", "payment.failed"}
    if event.event_type not in allowed_events:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported event type")

    with _LOCK:
        _WEBHOOK_EVENTS.append(event)

        intent = _PAYMENT_INTENTS.get(event.payment_intent_id)
        if intent is not None:
            _PAYMENT_INTENTS[event.payment_intent_id] = intent.model_copy(
                update={"status": event.status}
            )

        order = _get_order_or_404(event.order_id)
        order_status = "paid" if event.event_type == "payment.succeeded" else "payment_failed"
        _ORDERS[order.id] = order.model_copy(update={"status": order_status})

    return {
        "accepted": True,
        "event_type": event.event_type,
        "order_id": event.order_id,
        "order_status": _ORDERS[event.order_id].status,
    }
