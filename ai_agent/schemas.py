# schemas.py
from pydantic import BaseModel
from typing import List, Optional

class OrderItem(BaseModel):
    item_id: str
    quantity: int
    customizations: Optional[List[str]] = None

class Order(BaseModel):
    order_id: Optional[str] = None
    items: List[OrderItem]
    customer_id: str

class InventoryStatus(BaseModel):
    item_id: str
    in_stock: bool
    quantity_available: int

class PaymentRequest(BaseModel):
    order_id: str
    amount: float
    currency: str
    payment_token: str

class PaymentStatus(BaseModel):
    transaction_id: str
    status: str # e.g., "success", "failed"
    error_message: Optional[str] = None
