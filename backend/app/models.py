import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    Numeric,
    ForeignKey,
    DateTime,
    Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    logo_url = Column(String)
    cuisine = Column(String)
    rating = Column(Numeric(2, 1))
    location = Column(String, nullable=False)  # Made mandatory for delivery tracking
    address = Column(String, nullable=False)  # Full address for display
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    restaurant_admin_email = Column(String, unique=True, nullable=True)  # Email of restaurant admin
    restaurant_admin_hashed_password = Column(String, nullable=True)  # Password for restaurant admin
    menu_items = relationship("MenuItem", back_populates="restaurant")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, server_default='false', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Delivery address fields
    delivery_address = Column(Text, nullable=True)
    delivery_lat = Column(Numeric(10, 7), nullable=True)
    delivery_lng = Column(Numeric(10, 7), nullable=True)
    
    orders = relationship("Order", back_populates="customer")

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)
    
    restaurant_id = Column(UUID(as_uuid=True), ForeignKey("restaurants.id"), nullable=False)
    restaurant = relationship("Restaurant", back_populates="menu_items")
    
    inventory = relationship("Inventory", back_populates="menu_item", uselist=False)
    
    # THIS RELATIONSHIP IS NOW CORRECTLY DEFINED
    order_items = relationship("OrderItem", back_populates="menu_item")

class Inventory(Base):
    __tablename__ = "inventory"
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), primary_key=True)
    quantity = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    menu_item = relationship("MenuItem", back_populates="inventory")

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    status = Column(String, default="pending_payment", nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Delivery tracking fields
    delivery_address = Column(Text, nullable=True)  # Optional for cart, required at checkout
    delivery_lat = Column(Numeric(10, 7), nullable=True)
    delivery_lng = Column(Numeric(10, 7), nullable=True)
    driver_lat = Column(Numeric(10, 7), nullable=True)
    driver_lng = Column(Numeric(10, 7), nullable=True)
    delivery_status = Column(String, default="pending", nullable=True)
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    driver_name = Column(String, nullable=True)
    driver_phone = Column(String, nullable=True)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(UUID(as_uuid=True), ForeignKey("menu_items.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_time_of_order = Column(Numeric(10, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    
    # THIS RELATIONSHIP IS NOW CORRECTLY DEFINED
    menu_item = relationship("MenuItem", back_populates="order_items")