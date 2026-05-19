# ai_agent/main_orchestrator.py - NVIDIA NIM VERSION
import os
import sys
import json
import time
import inspect
import threading
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI

# Import local modules (try relative imports first, fall back to absolute)
try:
    from . import api_clients
    from . import tools
    from . import security
except ImportError:
    import api_clients
    import tools
    import security

# Thread-local storage for JWT tokens
_thread_local = threading.local()

# Enhanced response cache to reduce API calls (expires after 5 minutes)
_response_cache = {}
_cache_timeout = 300  # seconds
_cache_cleanup_interval = 60

# Request tracking for rate limiting
_request_tracker = {
    "last_request_time": 0,
    "request_count": 0,
    "window_start": time.time()
}

def get_cache_key(user_input: str, jwt_token: str) -> str:
    return f"{user_input[:20].lower().strip()}_{jwt_token[-10:]}"

def get_cached_response(cache_key: str):
    if cache_key in _response_cache:
        cached_data = _response_cache[cache_key]
        if time.time() - cached_data["timestamp"] < _cache_timeout:
            print(f"✅ Returning cached response (age: {int(time.time() - cached_data['timestamp'])}s)")
            return cached_data["response"]
        else:
            del _response_cache[cache_key]
    return None

def cache_response(cache_key: str, response: str):
    _response_cache[cache_key] = {
        "response": response,
        "timestamp": time.time()
    }
    current_time = time.time()
    expired_keys = [k for k, v in _response_cache.items()
                    if current_time - v["timestamp"] > _cache_timeout]
    for key in expired_keys:
        del _response_cache[key]
    print(f"📦 Cached response (cache size: {len(_response_cache)})")

# --- Configuration and Setup ---
load_dotenv()
nvidia_api_key = os.getenv("NVIDIA_API_KEY")

# NVIDIA NIM is OpenAI-compatible
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=nvidia_api_key,
)

# Model to use — llama-3.3-70b-instruct supports function calling well
NVIDIA_MODEL = "meta/llama-3.3-70b-instruct"

app = FastAPI(title="Food Butler AI Agent")

# Add CORS Middleware
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5502",
    "http://127.0.0.1:5502",
    "http://localhost:5503",
    "http://127.0.0.1:5503",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request, call_next):
    print(f"\n{'='*80}")
    print(f"📨 Incoming request: {request.method} {request.url.path}")
    print(f"🌐 Origin: {request.headers.get('origin', 'N/A')}")
    print(f"🔑 Authorization header present: {'Authorization' in request.headers}")
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith('Bearer '):
            token_preview = auth_header[7:27]
            print(f"🎫 Token preview: {token_preview}...")
        else:
            print(f"⚠️ Authorization header doesn't start with 'Bearer '")
    print(f"{'='*80}\n")
    response = await call_next(request)
    return response

def retry_nvidia_call(func, max_retries=5, base_delay=3):
    """Retry NVIDIA API calls with exponential backoff for rate limit errors."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_str = str(e)
            is_quota_error = (
                "429" in error_str or
                "quota" in error_str.lower() or
                "rate limit" in error_str.lower() or
                "resource exhausted" in error_str.lower()
            )
            if is_quota_error:
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    print(f"⚠️ NVIDIA API rate limit. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                    continue
                else:
                    print(f"❌ NVIDIA API rate limit after {max_retries} attempts. Using fallback response.")
                    return None
            else:
                raise e
    return None

# --- Tool Definitions in OpenAI JSON Schema format ---
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_restaurants",
            "description": "Get a list of all available restaurants.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_menu",
            "description": "Get the menu for a specific restaurant by its UUID, or list all available restaurants if no ID is given.",
            "parameters": {
                "type": "object",
                "properties": {
                    "restaurant_id": {
                        "type": "string",
                        "description": "The UUID of the restaurant. If omitted, returns all restaurants."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check the stock level for a specific menu item.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_id": {
                        "type": "string",
                        "description": "The UUID of the menu item."
                    }
                },
                "required": ["item_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_cart",
            "description": "Add a menu item to the user's cart.",
            "parameters": {
                "type": "object",
                "properties": {
                    "menu_item_id": {
                        "type": "string",
                        "description": "The UUID of the menu item to add."
                    },
                    "quantity": {
                        "type": "integer",
                        "description": "Number of items to add (default: 1)."
                    }
                },
                "required": ["menu_item_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_cart",
            "description": "Retrieve the current contents of the user's cart.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "checkout_cart",
            "description": "Process checkout for the user's current cart.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_history",
            "description": "Get the authenticated user's past order history.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place a direct order with a list of items.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "List of items with menu_item_id and quantity.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "menu_item_id": {"type": "string"},
                                "quantity": {"type": "integer"}
                            }
                        }
                    }
                },
                "required": ["items"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Check the current status of a specific order.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The UUID of the order."
                    }
                },
                "required": ["order_id"]
            }
        }
    },
]

# --- Tool Wrappers with Auto Token Injection ---
def get_current_token():
    return getattr(_thread_local, 'jwt_token', None)

def wrapped_get_restaurants():
    return tools.get_restaurants(token=get_current_token())

def wrapped_get_menu(restaurant_id: str = None):
    return tools.get_menu(restaurant_id=restaurant_id, token=get_current_token())

def wrapped_check_inventory(item_id: str):
    return tools.check_inventory(item_id=item_id, token=get_current_token())

def wrapped_place_order(items: list):
    return tools.place_order(items=items, token=get_current_token())

def wrapped_check_order_status(order_id: str):
    return tools.check_order_status(order_id=order_id, token=get_current_token())

def wrapped_add_to_cart(menu_item_id: str, quantity: int = 1):
    return tools.add_to_cart(menu_item_id=menu_item_id, quantity=quantity, token=get_current_token())

def wrapped_get_cart():
    return tools.get_cart(token=get_current_token())

def wrapped_checkout_cart():
    return tools.checkout_cart(token=get_current_token())

def wrapped_get_order_history():
    return tools.get_order_history(token=get_current_token())

# Map function names → callables for the agentic loop
TOOL_CALLABLES = {
    "get_restaurants": wrapped_get_restaurants,
    "get_menu": wrapped_get_menu,
    "check_inventory": wrapped_check_inventory,
    "add_to_cart": wrapped_add_to_cart,
    "get_cart": wrapped_get_cart,
    "checkout_cart": wrapped_checkout_cart,
    "get_order_history": wrapped_get_order_history,
    "place_order": wrapped_place_order,
    "check_order_status": wrapped_check_order_status,
}

def execute_tool_call(tool_name: str, tool_args: dict) -> str:
    """Execute a tool by name with the given arguments, return result as JSON string."""
    callable_fn = TOOL_CALLABLES.get(tool_name)
    if not callable_fn:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = callable_fn(**tool_args)
        return json.dumps(result) if not isinstance(result, str) else result
    except Exception as e:
        return json.dumps({"error": str(e)})

# --- System Prompt Template ---
SYSTEM_PROMPT_TEMPLATE = """
## 🚨🚨🚨 ABSOLUTE RULE - NEVER IGNORE RESTAURANT NAMES IN USER MESSAGE 🚨🚨🚨

⚠️⚠️⚠️ CRITICAL INSTRUCTION - READ THIS BEFORE DOING ANYTHING ⚠️⚠️⚠️

**IF THE USER'S MESSAGE CONTAINS A RESTAURANT NAME OR "from [restaurant]" - YOU MUST USE IT IMMEDIATELY!**
**NEVER, EVER ASK "WHICH RESTAURANT?" WHEN THE USER ALREADY TOLD YOU THE RESTAURANT!**

### STEP-BY-STEP WHEN USER SAYS "add [item] from [restaurant]":

1. **FIRST**: Read the entire user message and look for restaurant indicators:
   - "from [restaurant name]" → Restaurant is explicitly mentioned
   - "at [restaurant name]" → Restaurant is explicitly mentioned
   - Any restaurant name anywhere in message → USE IT

2. **SECOND**: If restaurant found in message:
   a. Call get_restaurants() tool to get full restaurant list
   b. Match user's restaurant name (fuzzy match OK: "chandrika" matches "Chandrika Tiffins")
   c. Get the restaurant's ID from the matched restaurant
   d. Call get_menu(restaurant_id=THE_UUID_NOT_NAME) to get menu
   e. Find the item they want in the menu
   f. Call add_to_cart(menu_item_id, quantity)
   g. Confirm the addition
   h. **NEVER ASK "WHICH RESTAURANT?" - THEY ALREADY TOLD YOU!**

3. **EXAMPLES OF RESTAURANT BEING SPECIFIED:**
   - "add 4 arabic chicken shawarma to the cart from chandrika tiffins" → Restaurant: Chandrika Tiffins
   - "order biryani from deccan spice" → Restaurant: Deccan Spice
   - "from chandrika" → Restaurant: Chandrika Family Restaurant (or Chandrika Tiffins)
   - "get pizza from mario" → Restaurant: Mario's

4. **FUZZY MATCHING IS ENCOURAGED:**
   - "chandrika" can match "Chandrika Tiffins" or "Chandrika Family Restaurant"
   - "deccan" matches "Deccan Spice"
   - If multiple matches, THEN ask which specific one
   - But if only one match, USE IT IMMEDIATELY

5. **WHAT YOU MUST NEVER DO:**
   ❌ User: "add 4 arabic chicken shawarma from chandrika tiffins"
   ❌ You: "I need to know which restaurant you would like to order from"
   ❌ This is WRONG WRONG WRONG - they just told you the restaurant!

6. **WHAT YOU MUST DO:**
   ✅ User: "add 4 arabic chicken shawarma from chandrika tiffins"
   ✅ You: *Calls get_restaurants* → *Finds "Chandrika Tiffins"* → *Gets restaurant_id* → *Calls get_menu(restaurant_id)* → *Finds arabic chicken shawarma* → *Calls add_to_cart* → "Perfect! Added 4x Arabic Chicken Shawarma from Chandrika Tiffins to your cart!"

## Persona
You are the Food Butler, an advanced AI-powered culinary concierge with deep expertise in food recommendations, dietary preferences, and personalized ordering. You are sophisticated, intuitive, and proactive in helping users discover and order food they'll love. You must always self-disclose that you are an AI assistant.

## Customer Context
Your instructions for this session are based on the following customer profile and order history:
---
{profile_context}
---

## Advanced Capabilities & Rules
1. **Smart Restaurant Selection:**
   - If message contains "from [restaurant name]" → USE THAT RESTAURANT immediately!
   - Check order history when user says "order [item]" without specifying a restaurant
   - Only ask for restaurant when item is ambiguous and not in history

2. **Intelligent Recommendations:**
   - Analyze order history to identify patterns (favorite cuisines, price ranges, dietary preferences)
   - Suggest complementary items (drinks with meals, appetizers, desserts)

3. **Proactive Ordering - BE DECISIVE:**
   - When user says "order [item]" or "add [item]": ACT IMMEDIATELY
   - Check order history, find restaurant/item, add to cart without unnecessary questions

4. **Smart Menu Navigation:**
   - STEP 1: Ask which restaurant (use get_menu to list restaurants)
   - STEP 2: Get menu from selected restaurant (use get_menu with restaurant_id)
   - STEP 3: Analyze history and suggest 2-3 specific items
   - Only show in-stock items returned by get_menu

5. **Order Management:**
   - You can add items to cart, check cart status, and help with checkout
   - ALWAYS use add_to_cart, get_cart, and checkout_cart tools
   - NEVER ask for tokens or authentication - it's handled automatically

6. **Tool Usage - CRITICAL:**
   - NEVER use restaurant NAME as restaurant_id - always use the UUID from get_restaurants
   - Example: get_menu(restaurant_id='a5e48e2b-fdd7-4e57-9fb1-0413c962ae5a') ✅
   - NOT: get_menu(restaurant_id='Deccan Spice') ❌

7. **Cart Display Format:**
   - Always display item ACTUAL NAME, quantity, price per item, line total, and grand total
   - NEVER say "menu item" - always use the actual item name

8. **Stock Availability:**
   - get_menu automatically filters out-of-stock items
   - If user requests an unavailable item: "I'm sorry, [item] is currently unavailable. Would you like similar items that are in stock?"

9. **Error Handling:**
   - If tools fail, explain clearly and offer alternatives
   - NEVER ask users to provide authentication tokens
"""

# --- API Request Models ---
class ChatRequest(BaseModel):
    user_input: str
    session_id: str

# --- Health Check ---
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Food Butler AI Agent (NVIDIA NIM)",
        "model": NVIDIA_MODEL,
        "timestamp": time.time()
    }

# --- Test Auth ---
@app.get("/test-auth")
async def test_auth(user_context: tuple[str, str] = Depends(security.get_current_user_context)):
    current_user_email, jwt_token = user_context
    return {
        "status": "authenticated",
        "user": current_user_email,
        "token_length": len(jwt_token),
        "message": "Authentication successful! ✅"
    }

# --- Main Chat Endpoint ---
@app.post("/chat")
async def handle_chat(
    request: ChatRequest,
    user_context: tuple[str, str] = Depends(security.get_current_user_context)
):
    current_user_email, jwt_token = user_context
    print(f"✅ --- Servicing authenticated request for user: {current_user_email} ---")
    print(f"📥 User input: {request.user_input[:50]}..." if len(request.user_input) > 50 else f"📥 User input: {request.user_input}")

    # Build profile context
    profile_context = f"Customer Profile: Not available for email {current_user_email}."
    try:
        profile = api_clients.get_customer_profile_by_email(current_user_email, token=jwt_token)
        order_history = api_clients.get_order_history(token=jwt_token)

        profile_data = {
            "customer_info": profile,
            "order_history": order_history,
            "analysis": {
                "total_orders": len(order_history) if isinstance(order_history, list) else 0,
                "favorite_items": [],
                "preferred_cuisines": [],
                "average_order_value": 0
            }
        }

        if isinstance(order_history, list) and len(order_history) > 0:
            total_value = 0
            item_counts = {}
            for order in order_history:
                if "items" in order and "total_price" in order:
                    total_value += float(order["total_price"])
                    for item in order["items"]:
                        if "menu_item" in item and "name" in item["menu_item"]:
                            item_name = item["menu_item"]["name"]
                            item_counts[item_name] = item_counts.get(item_name, 0) + item["quantity"]

            if len(order_history) > 0:
                profile_data["analysis"]["average_order_value"] = total_value / len(order_history)
            if item_counts:
                sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
                profile_data["analysis"]["favorite_items"] = [item[0] for item in sorted_items[:3]]

        profile_context = json.dumps(profile_data, indent=2)
    except Exception as e:
        print(f"Warning: Could not fetch customer profile or order history. {e}")

    # Store JWT token for tool auto-injection
    _thread_local.jwt_token = jwt_token
    print(f"--- Stored JWT token (length: {len(jwt_token) if jwt_token else 0}) ---")

    # Check cache
    cache_key = get_cache_key(request.user_input, jwt_token)
    cached_response = get_cached_response(cache_key)
    if cached_response:
        return {"response": cached_response}

    # Build messages for NVIDIA NIM
    final_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(profile_context=profile_context)
    messages = [
        {"role": "system", "content": final_system_prompt},
        {"role": "user", "content": request.user_input},
    ]

    try:
        # Agentic tool-call loop (NVIDIA NIM uses OpenAI-style tool calls)
        MAX_TOOL_ROUNDS = 10
        final_text = None

        for round_num in range(MAX_TOOL_ROUNDS):
            print(f"🔄 NVIDIA NIM call - round {round_num + 1}")

            def make_nvidia_call():
                return nvidia_client.chat.completions.create(
                    model=NVIDIA_MODEL,
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    max_tokens=2048,
                    temperature=0.6,
                )

            response = retry_nvidia_call(make_nvidia_call)

            if response is None:
                # Rate limit fallback
                user_input_lower = request.user_input.lower()
                if any(w in user_input_lower for w in ["menu", "show", "list", "items"]):
                    fallback_msg = "🍽️ I'm experiencing high demand right now. You can view restaurant menus by clicking on any restaurant card above."
                elif any(w in user_input_lower for w in ["restaurant", "where", "place"]):
                    fallback_msg = "🏪 I'm experiencing high demand right now. You can browse all available restaurants using the 'Restaurants' button in the navigation menu above."
                elif any(w in user_input_lower for w in ["cart", "checkout", "order"]):
                    fallback_msg = "🛒 I'm experiencing high demand right now. You can view and manage your cart by clicking the cart icon (🛒) in the top right corner."
                elif any(w in user_input_lower for w in ["history", "previous", "past"]):
                    fallback_msg = "📋 I'm experiencing high demand right now. You can view your order history by clicking the 'Orders' button in the navigation menu."
                else:
                    fallback_msg = "I'm currently experiencing high API usage. Please try again in a few minutes, or browse restaurants and menus using the navigation menu above."
                return {"response": fallback_msg}

            choice = response.choices[0]
            assistant_message = choice.message

            # Append assistant's response to message history
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in (assistant_message.tool_calls or [])
                ] or None
            })

            # Check if model wants to call tools
            if choice.finish_reason == "tool_calls" and assistant_message.tool_calls:
                print(f"🔧 Model requested {len(assistant_message.tool_calls)} tool call(s)")
                for tool_call in assistant_message.tool_calls:
                    fn_name = tool_call.function.name
                    try:
                        fn_args = json.loads(tool_call.function.arguments or "{}")
                    except json.JSONDecodeError:
                        fn_args = {}

                    print(f"  ▶ Calling tool: {fn_name}({fn_args})")
                    tool_result = execute_tool_call(fn_name, fn_args)
                    print(f"  ◀ Tool result: {tool_result[:200]}...")

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_result,
                    })
                # Continue loop to send tool results back to model
                continue

            # No more tool calls — extract final text
            final_text = assistant_message.content or ""
            break

        if not final_text:
            final_text = "I apologize, I was unable to process that request. Could you please rephrase?"

        cache_response(cache_key, final_text)
        return {"response": final_text}

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        error_str = str(e)
        is_quota_error = (
            "429" in error_str or
            "quota" in error_str.lower() or
            "rate limit" in error_str.lower() or
            "resource exhausted" in error_str.lower()
        )

        if is_quota_error:
            print(f"⚠️ NVIDIA API rate limit exceeded: {e}")
            user_input_lower = request.user_input.lower()
            if any(w in user_input_lower for w in ["menu", "show", "list", "items"]):
                fallback_msg = "🍽️ I'm experiencing high demand. You can view restaurant menus by clicking on any restaurant card above."
            elif any(w in user_input_lower for w in ["restaurant", "where", "place"]):
                fallback_msg = "🏪 I'm experiencing high demand. You can browse all available restaurants using the 'Restaurants' button in the navigation menu."
            elif any(w in user_input_lower for w in ["cart", "checkout", "order"]):
                fallback_msg = "🛒 I'm experiencing high demand. You can view and manage your cart by clicking the cart icon (🛒) in the top right."
            elif any(w in user_input_lower for w in ["history", "previous", "past"]):
                fallback_msg = "📋 I'm experiencing high demand. You can view your order history by clicking the 'Orders' button in the navigation menu."
            else:
                fallback_msg = "I'm experiencing high demand right now. Please try again in a moment, or browse restaurants and menus using the navigation menu above."
            return {"response": fallback_msg}
        else:
            print(f"❌ ERROR during NVIDIA NIM call: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# --- Main Block ---
if __name__ == "__main__":
    import uvicorn
    print("Starting Food Butler AI Agent server (NVIDIA NIM)...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
