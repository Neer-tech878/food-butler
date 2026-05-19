# api_clients.py
import os
import requests
from requests.exceptions import RequestException
from typing import List, Dict

# --- Configuration ---
BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")
print(f"--- API CLIENT: Using BACKEND_API_URL: {BASE_URL} ---")

def get_restaurants(token: str = None) -> dict:
    """Get list of all restaurants"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"--- API CLIENT: get_restaurants with token: {token[:20]}... ---")
        else:
            print("--- API CLIENT: get_restaurants WITHOUT token! ---")
        response = requests.get(f"{BASE_URL}/restaurants/", headers=headers)
        response.raise_for_status()
        return {"restaurants": response.json()}
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def get_restaurant_menu(restaurant_id: str, token: str = None) -> dict:
    """Get menu items from a specific restaurant"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"--- API CLIENT: get_restaurant_menu with token: {token[:20]}... ---")
        else:
            print("--- API CLIENT: get_restaurant_menu WITHOUT token! ---")
        response = requests.get(f"{BASE_URL}/restaurants/{restaurant_id}/menu", headers=headers)
        response.raise_for_status()
        return {"restaurant_id": restaurant_id, "menu_items": response.json()}
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        print(f"--- API CLIENT: Token was provided: {token is not None} ---")
        return {"error": "service_unavailable", "detail": str(e)}

def get_live_menu(token: str = None) -> dict:
    """Get all menu items (used for backward compatibility)"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(f"{BASE_URL}/menu", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        # Return a specific error structure our tool can handle
        return {"error": "service_unavailable", "detail": str(e)}

def check_live_inventory(item_id: str, token: str = None) -> dict:
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(f"{BASE_URL}/inventory/{item_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def place_live_order(items: List[Dict], token: str = None) -> dict:
    """Place an order with the given items"""
    print(f"--- API CLIENT: Place order - items count: {len(items) if items else 0}, has_token: {token is not None} ---")
    if token:
        print(f"--- API CLIENT: Token starts with: {token[:20]}... ---")
    
    # Format items for the API
    formatted_items = []
    for item in items:
        if isinstance(item, dict) and "menu_item_id" in item and "quantity" in item:
            formatted_items.append({
                "menu_item_id": item["menu_item_id"],
                "quantity": item["quantity"]
            })
    
    payload = {"items": formatted_items}
    print(f"--- API CLIENT: Payload: {payload} ---")
    try:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"--- API CLIENT: Authorization header set ---")
        
        print(f"--- API CLIENT: Making request to {BASE_URL}/orders/ ---")
        response = requests.post(f"{BASE_URL}/orders/", json=payload, headers=headers)
        print(f"--- API CLIENT: Response status: {response.status_code} ---")
        if response.status_code != 200:
            print(f"--- API CLIENT: Response headers: {dict(response.headers)} ---")
            print(f"--- API CLIENT: Response body: {response.text[:200]} ---")
        response.raise_for_status()
        result = response.json()
        print(f"--- API CLIENT: Success response ---")
        return result
    except RequestException as e:
        print(f"--- API CLIENT ERROR: {e} ---")
        return {"error": "service_unavailable", "detail": str(e)}

def process_live_payment(order_id: str, amount: float, token: str, auth_token: str = None) -> dict:
    payload = {"order_id": order_id, "amount": amount, "token": token}
    try:
        headers = {"Content-Type": "application/json"}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        response = requests.post(f"{BASE_URL}/payments/charge", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def get_customer_profile(customer_id: str, token: str = None) -> dict:
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(f"{BASE_URL}/customers/{customer_id}", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def get_order_status(order_id: str, token: str = None) -> dict:
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(f"{BASE_URL}/orders/{order_id}/status", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def get_customer_profile_by_email(email: str, token: str = None) -> dict:
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        response = requests.get(f"{BASE_URL}/customers/email/{email}", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def add_to_cart(menu_item_id: str, quantity: int = 1, token: str = None) -> dict:
    """Add item to shopping cart"""
    print(f"--- API CLIENT: Adding to cart - item: {menu_item_id}, quantity: {quantity}, has_token: {token is not None} ---")
    try:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        payload = {
            "menu_item_id": menu_item_id,
            "quantity": quantity
        }
        
        print(f"--- API CLIENT: Making request to {BASE_URL}/cart/items ---")
        response = requests.post(f"{BASE_URL}/cart/items", json=payload, headers=headers)
        print(f"--- API CLIENT: Response status: {response.status_code} ---")
        response.raise_for_status()
        result = response.json()
        print(f"--- API CLIENT: Success response: {result} ---")
        return result
    except RequestException as e:
        print(f"--- API CLIENT ERROR: {e} ---")
        return {"error": "service_unavailable", "detail": str(e)}

def get_cart(token: str = None) -> dict:
    """Get current shopping cart contents"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.get(f"{BASE_URL}/cart/", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}

def checkout_cart(token: str = None) -> dict:
    """Checkout the current cart"""
    print(f"--- API CLIENT: Checkout cart - has_token: {token is not None} ---")
    if token:
        print(f"--- API CLIENT: Token starts with: {token[:20]}... ---")
    try:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"--- API CLIENT: Authorization header set ---")
        
        print(f"--- API CLIENT: Making request to {BASE_URL}/cart/checkout ---")
        response = requests.post(f"{BASE_URL}/cart/checkout", headers=headers)
        print(f"--- API CLIENT: Response status: {response.status_code} ---")
        if response.status_code != 200:
            print(f"--- API CLIENT: Response headers: {dict(response.headers)} ---")
            print(f"--- API CLIENT: Response body: {response.text[:200]} ---")
        response.raise_for_status()
        result = response.json()
        print(f"--- API CLIENT: Success response ---")
        return result
    except RequestException as e:
        print(f"--- API CLIENT ERROR: {e} ---")
        return {"error": "service_unavailable", "detail": str(e)}

def get_order_history(token: str = None) -> dict:
    """Get user's order history"""
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = requests.get(f"{BASE_URL}/orders/me/", headers=headers)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        print(f"API CLIENT ERROR: {e}")
        return {"error": "service_unavailable", "detail": str(e)}