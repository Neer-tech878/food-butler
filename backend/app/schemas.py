import uuid
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

# ===============================================
# Restaurant Schemas
# ===============================================
class RestaurantBase(BaseModel):
    name: str
    logo_url: Optional[str] = None
    cuisine: Optional[str] = None
    rating: Optional[float] = None
    location: str  # Made mandatory for delivery tracking
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class RestaurantCreate(RestaurantBase):
    restaurant_admin_email: Optional[str] = None
    restaurant_admin_password: Optional[str] = None

class Restaurant(RestaurantBase):
    id: uuid.UUID
    restaurant_admin_email: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    logo_url: Optional[str] = None
    cuisine: Optional[str] = None
    rating: Optional[float] = None
    location: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    restaurant_admin_email: Optional[str] = None
    restaurant_admin_password: Optional[str] = None

# ===============================================
# MenuItem Schemas
# ===============================================
class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    restaurant_id: uuid.UUID

class MenuItem(MenuItemBase):
    id: uuid.UUID
    restaurant_id: uuid.UUID
    inventory: Optional['Inventory'] = None
    model_config = ConfigDict(from_attributes=True)

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

# ===============================================
# Customer Schemas
# ===============================================
class CustomerBase(BaseModel):
    name: str
    email: str

class CustomerCreate(CustomerBase):
    password: str

class CustomerAddressUpdate(BaseModel):
    delivery_address: str
    delivery_lat: float
    delivery_lng: float

# A simple Customer schema for nesting inside Order, breaking the loop
class CustomerInOrder(CustomerBase):
    id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

# ===============================================
# Restaurant Admin Schemas
# ===============================================
class RestaurantAdminLogin(BaseModel):
    email: str
    password: str
class OrderItemBase(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

# THIS IS THE CLASS THAT WAS MISSING
class OrderItemUpdate(BaseModel):
    quantity: int

class OrderItem(OrderItemBase):
    id: uuid.UUID
    price_at_time_of_order: float
    menu_item: MenuItem
    model_config = ConfigDict(from_attributes=True)

# ===============================================
# Order Schemas
# ===============================================
class Order(BaseModel):
    id: uuid.UUID
    status: str
    total_price: float
    created_at: datetime
    items: List[OrderItem] = []
    customer: CustomerInOrder # Use the simple customer schema here
    
    # Delivery tracking fields
    delivery_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    driver_lat: Optional[float] = None
    driver_lng: Optional[float] = None
    delivery_status: Optional[str] = "pending"
    estimated_delivery_time: Optional[datetime] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
    
class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    delivery_address: str  # Made mandatory for delivery
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None

# Delivery tracking schemas
class DeliveryLocationUpdate(BaseModel):
    driver_lat: float
    driver_lng: float

class DeliveryStatusUpdate(BaseModel):
    delivery_status: str
    estimated_delivery_time: Optional[datetime] = None

class OrderTrackingInfo(BaseModel):
    order_id: uuid.UUID
    status: str
    delivery_status: str
    delivery_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    driver_lat: Optional[float] = None
    driver_lng: Optional[float] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    estimated_delivery_time: Optional[datetime] = None
    created_at: datetime

# ===============================================
# FULL Customer Schema (for GET /customers/me)
# ===============================================
class Customer(CustomerBase):
    id: uuid.UUID
    created_at: datetime
    is_admin: bool = False
    delivery_address: Optional[str] = None
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    orders: List[Order] = []
    model_config = ConfigDict(from_attributes=True)

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    is_admin: Optional[bool] = None
class Token(BaseModel):
    access_token: str
    token_type: str

class RestaurantAdminToken(Token):
    restaurant_id: uuid.UUID
    restaurant_name: str

class TokenData(BaseModel):
    email: Optional[str] = None
class CustomerPasswordUpdate(BaseModel):
    new_password: str

# ===============================================
# Inventory Schema
# ===============================================
class InventoryCreate(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int

class Inventory(BaseModel):
    menu_item_id: uuid.UUID
    quantity: int
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Resolve forward references
MenuItem.model_rebuild()