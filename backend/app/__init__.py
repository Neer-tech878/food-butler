# food_butler_backend/app/__init__.py

# Import all models to ensure they are registered with SQLAlchemy's Base
from .models import Customer, MenuItem, Inventory, Order, OrderItem, Restaurant