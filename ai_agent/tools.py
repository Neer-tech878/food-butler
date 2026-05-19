# tools.py
import os
import sys
from typing import List, Dict

# Import local modules (try relative imports first, fall back to absolute)
try:
    from . import api_clients
except ImportError:
    # Fallback for when run as script
    import api_clients

def get_restaurants(token: str = None) -> dict:
    """
    Retrieves the list of all available restaurants. Call this tool FIRST when user wants to order
    to show them which restaurants are available.
    """
    print("--- TOOL: Calling get_restaurants API client ---")
    return api_clients.get_restaurants(token=token)

def get_menu(restaurant_id: str = None, token: str = None) -> dict:
    """
    Retrieves ONLY available and in-stock menu items from a specific restaurant or all menu items.
    Items without stock or marked as unavailable are automatically filtered out.
    Args:
        restaurant_id: Optional - The UUID (NOT name) of the restaurant. Example: 'a5e48e2b-fdd7-4e57-9fb1-0413c962ae5a'. 
                      You must use the 'id' field from get_restaurants response, NOT the 'name' field.
                      If not provided, returns all items from all restaurants.
        token: Authentication token
    Call this tool after user selects a restaurant. Use the restaurant's UUID from get_restaurants response.
    NOTE: This tool ONLY returns items that are currently available and in stock.
    """
    if restaurant_id:
        print(f"--- TOOL: Calling get_restaurant_menu API client for restaurant: {restaurant_id} ---")
        result = api_clients.get_restaurant_menu(restaurant_id, token=token)
    else:
        print("--- TOOL: Calling get_menu API client (all items) ---")
        result = api_clients.get_live_menu(token=token)
    
    # Double-check filtering on the client side for safety
    if isinstance(result, dict) and "menu_items" in result:
        # Filter out items that are not available
        available_items = [item for item in result["menu_items"] if item.get("is_available", True)]
        result["menu_items"] = available_items
        result["note"] = "Only showing items that are currently available and in stock"
        print(f"--- TOOL: Filtered menu to {len(available_items)} available items ---")
    elif isinstance(result, list):
        # Handle case where result is directly a list
        available_items = [item for item in result if item.get("is_available", True)]
        result = available_items
        print(f"--- TOOL: Filtered menu to {len(available_items)} available items ---")
    
    return result

def check_inventory(item_id: str, token: str = None) -> dict:
    """
    Checks the current stock level for a given menu item ID.
    """
    print(f"--- TOOL: Calling check_inventory API client for item: {item_id} ---")
    return api_clients.check_live_inventory(item_id, token=token)

def place_order(items: List[Dict], token: str = None) -> dict:
    """
    Places an order for a list of items. Each item should be a dictionary
    with 'item_id' and 'quantity'.
    """
    print(f"--- TOOL: Calling place_order API client with items: {items} ---")
    return api_clients.place_live_order(items, token=token)

def process_payment(order_id: str, amount: float, payment_token: str, auth_token: str = None) -> dict:
    """
    Processes a payment for a given order using a payment token.
    """
    print(f"--- TOOL: Calling process_payment API client for order: {order_id} ---")
    return api_clients.process_live_payment(order_id, amount, payment_token, auth_token=auth_token)

def check_order_status(order_id: str, token: str = None) -> dict:
    """
    Checks the status of a previously placed order using its order ID.
    """
    print(f"--- TOOL: Calling get_order_status API client for order: {order_id} ---")
    return api_clients.get_order_status(order_id, token=token)

def add_to_cart(menu_item_id: str, quantity: int = 1, token: str = None) -> dict:
    """
    Adds a specific menu item to the user's shopping cart.
    Args:
        menu_item_id: The ID of the menu item to add
        quantity: How many of this item to add (default: 1)
        token: Authentication token
    """
    print(f"--- TOOL: Adding {quantity}x item {menu_item_id} to cart ---")
    
    # Validate menu_item_id format
    try:
        import uuid
        uuid.UUID(menu_item_id)  # Validate it's a valid UUID
    except ValueError:
        return {"error": "invalid_menu_item_id", "detail": f"Menu item ID '{menu_item_id}' is not a valid UUID", "menu_item_id": menu_item_id}
    
    if quantity <= 0:
        return {"error": "invalid_quantity", "detail": f"Quantity must be positive, got {quantity}"}
    
    try:
        result = api_clients.add_to_cart(menu_item_id, quantity, token=token)
        print(f"--- TOOL: Cart add result: {result} ---")
        return result
    except Exception as e:
        print(f"--- TOOL ERROR: Failed to add to cart: {e} ---")
        return {"error": "cart_add_failed", "detail": str(e), "menu_item_id": menu_item_id, "quantity": quantity}

def get_cart(token: str = None) -> dict:
    """
    Retrieves the current contents of the user's shopping cart with formatted item details.
    Returns cart with items showing: item name, quantity, individual price, and line total.
    Total cart price is also included.
    """
    print("--- TOOL: Getting current cart contents ---")
    cart_data = api_clients.get_cart(token=token)
    
    # Add formatted summary for better AI understanding
    if cart_data and "items" in cart_data and len(cart_data["items"]) > 0:
        cart_summary = []
        for item in cart_data["items"]:
            if "menu_item" in item:
                item_name = item["menu_item"].get("name", "Unknown Item")
                quantity = item.get("quantity", 1)
                price_per_item = float(item.get("price_at_time_of_order", 0))
                line_total = price_per_item * quantity
                
                cart_summary.append({
                    "item_name": item_name,
                    "quantity": quantity,
                    "price_per_item": price_per_item,
                    "line_total": line_total
                })
        
        cart_data["formatted_summary"] = {
            "items": cart_summary,
            "total_items": sum(item["quantity"] for item in cart_summary),
            "cart_total": float(cart_data.get("total_price", 0))
        }
    
    return cart_data

def checkout_cart(token: str = None) -> dict:
    """
    Processes checkout for the current cart, creating a pending order.
    """
    print("--- TOOL: Processing cart checkout ---")
    return api_clients.checkout_cart(token=token)

def get_order_history(token: str = None) -> dict:
    """
    Retrieves the user's complete order history for analysis and recommendations.
    """
    print("--- TOOL: Fetching user order history ---")
    return api_clients.get_order_history(token=token)