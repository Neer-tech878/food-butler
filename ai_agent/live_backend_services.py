# live_backend_services.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uuid

app = FastAPI()

# --- In-Memory Database (Simulating real backend systems) ---
DB = {
    "menu": {
        "items": [
            {"item_id": "pizza-margherita", "name": "Margherita Pizza", "price": 12.50},
            {"item_id": "salad-mediterranean", "name": "Mediterranean Salad", "price": 9.75},
            {"item_id": "pasta-carbonara", "name": "Pasta Carbonara", "price": 15.00},
            {"item_id": "drink-soda", "name": "Soda", "price": 2.50}
        ]
    },
    "inventory": {
        "pizza-margherita": 50,
        "salad-mediterranean": 0, # Out of stock
        "pasta-carbonara": 30,
        "drink-soda": 100
    },
    "orders": {},
    "customers": {
        "user123": {
            "name": "Jaswanth",
            "preferences": {
                "dietary_goals": ["low-carb", "high-protein"],
                "spice_level": "medium"
            },
            "purchase_history": [
                {"item_id": "pasta-carbonara", "quantity": 1},
                {"item_id": "drink-soda", "quantity": 2}
            ]
        }
    }
}

# --- API Endpoints ---

@app.get("/menu")
async def get_menu():
    """Returns the full menu."""
    return DB["menu"]

@app.get("/inventory/{item_id}")
async def get_inventory(item_id: str):
    """Checks inventory for a specific item."""
    if item_id not in DB["inventory"]:
        raise HTTPException(status_code=404, detail="Item not found")

    quantity = DB["inventory"][item_id]
    return {"item_id": item_id, "in_stock": quantity > 0, "quantity_available": quantity}

class OrderItem(BaseModel):
    item_id: str
    quantity: int

class OrderRequest(BaseModel):
    items: List[OrderItem]
    customer_id: str

@app.post("/orders", status_code=201)
async def create_order(order_request: OrderRequest):
    """Creates a new order in the system."""
    order_id = f"ord_{uuid.uuid4().hex[:8]}"
    total_price = 0

    # Check stock and calculate total price
    for item in order_request.items:
        if item.item_id not in DB["inventory"] or DB["inventory"][item.item_id] < item.quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {item.item_id}")

        menu_item = next((m for m in DB["menu"]["items"] if m["item_id"] == item.item_id), None)
        total_price += menu_item["price"] * item.quantity

    DB["orders"][order_id] = {
        "details": order_request.model_dump(),
        "status": "pending_payment",
        "total_price": total_price
    }
    return {"order_id": order_id, "status": "pending_payment", "total_price": total_price}

class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    token: str

@app.post("/payments/charge")
async def process_payment(payment_request: PaymentRequest):
    """Processes a payment for an order."""
    order_id = payment_request.order_id
    if order_id not in DB["orders"]:
        raise HTTPException(status_code=404, detail="Order not found")

    if "declined" in payment_request.token:
        raise HTTPException(status_code=400, detail="Payment declined by bank: Insufficient funds")

    if "invalid" in payment_request.token:
        raise HTTPException(status_code=400, detail="Payment declined: Invalid token")

    DB["orders"][order_id]["status"] = "confirmed"
    transaction_id = f"txn_{uuid.uuid4().hex[:12]}"
    return {"transaction_id": transaction_id, "status": "success"}

@app.get("/customers/{customer_id}")
async def get_customer_profile(customer_id: str):
    """Retrieves a customer's profile."""
    if customer_id not in DB["customers"]:
        raise HTTPException(status_code=404, detail="Customer not found")
    return DB["customers"][customer_id]

@app.get("/orders/{order_id}/status")
async def get_order_status(order_id: str):
    """Returns the current status of an order."""
    if order_id not in DB["orders"]:
        raise HTTPException(status_code=404, detail="Order not found")

    # Simulate status for a confirmed order
    status = DB["orders"][order_id].get("status", "unknown")
    if status == "confirmed":
        status = "preparing" # Pretend it's being made

    return {"order_id": order_id, "status": status}