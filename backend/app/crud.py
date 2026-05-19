from sqlalchemy.orm import Session, joinedload
from . import models, schemas
import uuid

# ===============================================
# Restaurant CRUD Functions
# ===============================================

def get_restaurant(db: Session, restaurant_id: uuid.UUID):
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()

def get_restaurants(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Restaurant).offset(skip).limit(limit).all()

def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    from . import security
    restaurant_data = restaurant.model_dump()
    
    # Hash restaurant admin password if provided
    if restaurant_data.get('restaurant_admin_password'):
        restaurant_data['restaurant_admin_hashed_password'] = security.get_password_hash(restaurant_data.pop('restaurant_admin_password'))
    
    db_restaurant = models.Restaurant(**restaurant_data)
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def update_restaurant(db: Session, restaurant_id: uuid.UUID, restaurant: schemas.RestaurantUpdate):
    from . import security
    db_restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not db_restaurant:
        return None
    
    update_data = restaurant.model_dump(exclude_unset=True)
    
    # Hash restaurant admin password if provided
    if update_data.get('restaurant_admin_password'):
        update_data['restaurant_admin_hashed_password'] = security.get_password_hash(update_data.pop('restaurant_admin_password'))
    
    for field, value in update_data.items():
        setattr(db_restaurant, field, value)
    
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def delete_restaurant(db: Session, restaurant_id: uuid.UUID):
    db_restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if not db_restaurant:
        return False
    
    db.delete(db_restaurant)
    db.commit()
    return True

def get_restaurant_by_admin_email(db: Session, email: str):
    return db.query(models.Restaurant).filter(models.Restaurant.restaurant_admin_email == email).first()

def authenticate_restaurant_admin(db: Session, email: str, password: str):
    from . import security
    restaurant = get_restaurant_by_admin_email(db, email)
    if not restaurant or not restaurant.restaurant_admin_hashed_password:
        return None
    if not security.verify_password(password, restaurant.restaurant_admin_hashed_password):
        return None
    return restaurant

def update_restaurant_admin_password(db: Session, restaurant_id: uuid.UUID, hashed_password: str):
    db_restaurant = get_restaurant(db, restaurant_id)
    if not db_restaurant:
        return None
    db_restaurant.restaurant_admin_hashed_password = hashed_password
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

# ===============================================
# MenuItem CRUD Functions
# ===============================================

def get_menu_item(db: Session, menu_item_id: uuid.UUID):
    return db.query(models.MenuItem).filter(models.MenuItem.id == menu_item_id).first()

def get_menu_items(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all menu items, filtering out unavailable items and items without stock.
    """
    all_menu_items = db.query(models.MenuItem).offset(skip).limit(limit).all()
    
    # Filter items that are available and have stock
    available_items = []
    for item in all_menu_items:
        if not item.is_available:
            continue
        # Check inventory
        inventory = db.query(models.Inventory).filter(
            models.Inventory.menu_item_id == item.id
        ).first()
        if inventory and inventory.quantity > 0:
            available_items.append(item)
        elif not inventory:  # If no inventory record, assume available (for backward compatibility)
            available_items.append(item)
    
    return available_items

def get_menu_items_by_restaurant(db: Session, restaurant_id: uuid.UUID):
    menu_items = db.query(models.MenuItem).options(
        joinedload(models.MenuItem.inventory)
    ).filter(
        models.MenuItem.restaurant_id == restaurant_id
    ).all()
    
    # Return all items with their inventory loaded
    # Frontend or business logic can filter by availability and stock if needed
    return menu_items

def create_menu_item(db: Session, menu_item: schemas.MenuItemCreate):
    db_menu_item = models.MenuItem(**menu_item.model_dump())
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

def update_menu_item(db: Session, menu_item_id: uuid.UUID, menu_item: schemas.MenuItemUpdate):
    db_item = get_menu_item(db, menu_item_id=menu_item_id)
    if not db_item:
        return None
    update_data = menu_item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_menu_item(db: Session, menu_item_id: uuid.UUID):
    db_item = get_menu_item(db, menu_item_id=menu_item_id)
    if not db_item:
        return False
    db.delete(db_item)  # Hard delete instead of soft delete
    db.commit()
    return True

# ===============================================
# Customer CRUD Functions
# ===============================================

def get_customer(db: Session, customer_id: uuid.UUID):
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()

def get_customer_by_email(db: Session, email: str):
    return db.query(models.Customer).filter(models.Customer.email == email).first()

def create_customer(db: Session, customer: schemas.CustomerCreate, hashed_password: str, is_admin: bool = False):
    db_customer = models.Customer(
        name=customer.name, 
        email=customer.email, 
        hashed_password=hashed_password,
        is_admin=is_admin
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer_password(db: Session, customer: models.Customer, hashed_password: str):
    customer.hashed_password = hashed_password
    db.commit()
    db.refresh(customer)
    return customer

def update_customer_address(db: Session, customer: models.Customer, delivery_address: str, delivery_lat: float, delivery_lng: float):
    customer.delivery_address = delivery_address
    customer.delivery_lat = delivery_lat
    customer.delivery_lng = delivery_lng
    db.commit()
    db.refresh(customer)
    return customer

def get_all_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Customer).offset(skip).limit(limit).all()

def update_customer(db: Session, customer_id: uuid.UUID, customer_update: dict):
    db_customer = get_customer(db, customer_id=customer_id)
    if not db_customer:
        return None
    
    for key, value in customer_update.items():
        if hasattr(db_customer, key):
            setattr(db_customer, key, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: uuid.UUID):
    db_customer = get_customer(db, customer_id=customer_id)
    if not db_customer:
        return False
    
    db.delete(db_customer)
    db.commit()
    return True

def get_order(db: Session, order_id: uuid.UUID):
    return db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.menu_item),
        joinedload(models.Order.customer)
    ).filter(models.Order.id == order_id).first()

def create_order(db: Session, order: schemas.OrderCreate, customer_id: uuid.UUID):
    """Create a new order with the given items."""
    total_price = 0
    
    # Validate all items and calculate total price
    for item_data in order.items:
        menu_item = get_menu_item(db, menu_item_id=item_data.menu_item_id)
        if not menu_item or not menu_item.is_available:
            raise ValueError(f"Menu item {item_data.menu_item_id} is not available")
        total_price += menu_item.price * item_data.quantity
    
    # Create the order with delivery information
    db_order = models.Order(
        customer_id=customer_id,
        status="pending_payment",
        total_price=total_price,
        delivery_address=order.delivery_address,
        delivery_lat=order.delivery_lat,
        delivery_lng=order.delivery_lng,
        delivery_status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Add order items
    for item_data in order.items:
        menu_item = get_menu_item(db, menu_item_id=item_data.menu_item_id)
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            menu_item_id=item_data.menu_item_id,
            quantity=item_data.quantity,
            price_at_time_of_order=menu_item.price
        )
        db.add(db_order_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).options(
        joinedload(models.Order.customer),
        joinedload(models.Order.items).joinedload(models.OrderItem.menu_item)
    ).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def get_orders_by_customer(db: Session, customer_id: uuid.UUID):
    return db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.menu_item)
    ).filter(models.Order.customer_id == customer_id).order_by(models.Order.created_at.desc()).all()

# ===============================================
# Cart CRUD Functions
# ===============================================

def get_active_cart_by_customer(db: Session, customer_id: uuid.UUID):
    return db.query(models.Order).options(
        joinedload(models.Order.items).joinedload(models.OrderItem.menu_item)
    ).filter(models.Order.customer_id == customer_id, models.Order.status == 'cart').first()

def add_item_to_cart(db: Session, customer_id: uuid.UUID, item: schemas.OrderItemCreate):
    cart = get_active_cart_by_customer(db, customer_id=customer_id)
    if not cart:
        cart = models.Order(customer_id=customer_id, status='cart', total_price=0)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    menu_item = get_menu_item(db, menu_item_id=item.menu_item_id)
    if not menu_item:
        raise ValueError(f"Menu item {item.menu_item_id} does not exist.")
    if not menu_item.is_available:
        raise ValueError(f"Menu item {item.menu_item_id} is not available.")

    # Check inventory before adding to cart
    inventory = db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == item.menu_item_id
    ).first()
    
    if inventory:
        # Check if there's enough inventory for the requested quantity
        current_cart_quantity = 0
        existing_item = db.query(models.OrderItem).filter(
            models.OrderItem.order_id == cart.id,
            models.OrderItem.menu_item_id == item.menu_item_id
        ).first()
        if existing_item:
            current_cart_quantity = existing_item.quantity
        
        if inventory.quantity < (current_cart_quantity + item.quantity):
            raise ValueError(f"Insufficient inventory. Only {inventory.quantity} items available, you have {current_cart_quantity} in cart, trying to add {item.quantity}.")
    # If no inventory record exists, assume unlimited stock (backward compatibility)

    # Check if item is already in cart, if so, update quantity
    existing_item = db.query(models.OrderItem).filter(
        models.OrderItem.order_id == cart.id,
        models.OrderItem.menu_item_id == item.menu_item_id
    ).first()

    if existing_item:
        existing_item.quantity += item.quantity
    else:
        db_order_item = models.OrderItem(
            order_id=cart.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity,
            price_at_time_of_order=menu_item.price
        )
        db.add(db_order_item)
    
    # Recalculate total price for entire cart
    total_price = 0
    for order_item in cart.items:
        total_price += order_item.price_at_time_of_order * order_item.quantity
    cart.total_price = total_price
    
    db.commit()
    db.refresh(cart)
    return cart

def update_cart_item_quantity(db: Session, customer_id: uuid.UUID, order_item_id: uuid.UUID, quantity: int):
    cart = get_active_cart_by_customer(db, customer_id=customer_id)
    if not cart:
        raise ValueError("No active cart found.")
    
    item_to_update = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id, models.OrderItem.order_id == cart.id).first()
    if not item_to_update:
        raise ValueError("Item not found in cart.")

    if quantity <= 0:
        return remove_item_from_cart(db, customer_id, order_item_id)

    # Check inventory before updating quantity
    inventory = db.query(models.Inventory).filter(
        models.Inventory.menu_item_id == item_to_update.menu_item_id
    ).first()
    
    if inventory and inventory.quantity < quantity:
        raise ValueError(f"Insufficient inventory. Only {inventory.quantity} items available.")

    item_to_update.quantity = quantity
    
    # Recalculate total
    new_total = 0
    for item in cart.items:
        new_total += item.price_at_time_of_order * item.quantity
    cart.total_price = new_total
    
    db.commit()
    db.refresh(cart)
    return cart

def remove_item_from_cart(db: Session, customer_id: uuid.UUID, order_item_id: uuid.UUID):
    cart = get_active_cart_by_customer(db, customer_id=customer_id)
    if not cart:
        raise ValueError("No active cart found.")
        
    item_to_remove = db.query(models.OrderItem).filter(models.OrderItem.id == order_item_id, models.OrderItem.order_id == cart.id).first()
    if not item_to_remove:
        raise ValueError("Item not found in cart.")

    cart.total_price -= item_to_remove.price_at_time_of_order * item_to_remove.quantity
    db.delete(item_to_remove)
    db.commit()
    db.refresh(cart)
    return cart

def checkout_cart(db: Session, customer_id: uuid.UUID, delivery_address=None, delivery_lat=None, delivery_lng=None):
    cart = get_active_cart_by_customer(db, customer_id=customer_id)
    if not cart or not cart.items:
        raise ValueError("Cart is empty or not found.")

    for item in cart.items:
        inventory_item = db.query(models.Inventory).filter(models.Inventory.menu_item_id == item.menu_item_id).first()
        if not inventory_item or inventory_item.quantity < item.quantity:
            raise ValueError(f"Not enough stock for item {item.menu_item.name}. Please update your cart.")
    
    cart.status = 'pending_payment'
    cart.delivery_address = delivery_address
    cart.delivery_lat = delivery_lat
    cart.delivery_lng = delivery_lng
    cart.delivery_status = 'pending'
    db.commit()
    db.refresh(cart)
    return cart

# ===============================================
# Admin & Inventory CRUD Functions
# ===============================================

def create_or_update_inventory(db: Session, inventory: schemas.InventoryCreate):
    db_inventory = db.query(models.Inventory).filter(models.Inventory.menu_item_id == inventory.menu_item_id).first()
    if db_inventory:
        db_inventory.quantity = inventory.quantity
    else:
        db_inventory = models.Inventory(**inventory.model_dump())
        db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).options(
        joinedload(models.Order.customer)
    ).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def update_order_status(db: Session, order_id: uuid.UUID, new_status: str):
    db_order = get_order(db, order_id=order_id)
    if not db_order:
        return None
    
    # If order is being confirmed, reduce inventory
    if new_status in ['confirmed', 'preparing', 'completed'] and db_order.status not in ['confirmed', 'preparing', 'completed']:
        for item in db_order.items:
            inventory_item = db.query(models.Inventory).filter(models.Inventory.menu_item_id == item.menu_item_id).first()
            if inventory_item:
                inventory_item.quantity -= item.quantity
                if inventory_item.quantity < 0:
                    inventory_item.quantity = 0  # Prevent negative inventory
    
    db_order.status = new_status
    db.commit()
    db.refresh(db_order)
    return db_order

# ===============================================
# Delivery Tracking CRUD Functions
# ===============================================

def update_driver_location(db: Session, order_id: uuid.UUID, driver_lat: float, driver_lng: float):
    """Update the driver's current location for an order."""
    db_order = get_order(db, order_id=order_id)
    if not db_order:
        return None
    
    db_order.driver_lat = driver_lat
    db_order.driver_lng = driver_lng
    db.commit()
    db.refresh(db_order)
    return db_order

def update_delivery_status(db: Session, order_id: uuid.UUID, delivery_status: str, estimated_delivery_time=None):
    """Update the delivery status and estimated delivery time."""
    db_order = get_order(db, order_id=order_id)
    if not db_order:
        return None
    
    db_order.delivery_status = delivery_status
    if estimated_delivery_time:
        db_order.estimated_delivery_time = estimated_delivery_time
    
    db.commit()
    db.refresh(db_order)
    return db_order

def assign_driver_to_order(db: Session, order_id: uuid.UUID, driver_name: str, driver_phone: str):
    """Assign a driver to an order."""
    db_order = get_order(db, order_id=order_id)
    if not db_order:
        return None
    
    db_order.driver_name = driver_name
    db_order.driver_phone = driver_phone
    db_order.delivery_status = "assigned"
    
    db.commit()
    db.refresh(db_order)
    return db_order

def get_order_tracking_info(db: Session, order_id: uuid.UUID):
    """Get tracking information for an order."""
    return get_order(db, order_id=order_id)