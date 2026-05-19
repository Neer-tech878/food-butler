# mock_agents.py
from fastapi import FastAPI
from pydantic import BaseModel
import tools

app = FastAPI()

# --- Inventory Agent Endpoint ---
class InventoryCheckRequest(BaseModel):
    item_id: str

@app.post("/inventory/check")
async def inventory_check_endpoint(request: InventoryCheckRequest):
    """Endpoint for the Inventory Executor Agent."""
    return tools.check_inventory(item_id=request.item_id)


# --- Payment Agent Endpoint ---
class PaymentProcessRequest(BaseModel):
    order_id: str
    amount: float
    payment_token: str

@app.post("/payment/process")
async def process_payment_endpoint(request: PaymentProcessRequest):
    """Endpoint for the Payment Executor Agent."""
    return tools.process_payment(
        order_id=request.order_id, 
        amount=request.amount,
        payment_token=request.payment_token
    )

# --- Menu Agent (Placeholder) ---
@app.get("/menu/items")
async def get_menu():
    """Placeholder for the Menu Agent."""
    return {"items": [
        {"item_id": "pizza-margherita", "name": "Margherita Pizza", "price": 12.50},
        {"item_id": "salad-mediterranean", "name": "Mediterranean Salad", "price": 9.75},
    ]}


# --- Menu Agent ---
@app.get("/menu")
async def get_menu_endpoint():
    """Endpoint for the Menu Executor Agent."""
    return tools.get_menu()