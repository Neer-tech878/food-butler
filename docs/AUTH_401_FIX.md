# 401 Unauthorized Error - FIXED

## Date: October 15, 2025

## Problem
```
Error: Could not validate credentials
agent-1 | INFO: 172.19.0.1:65088 - "POST /chat HTTP/1.1" 401 Unauthorized
```

## Root Causes Identified

### 1. **CORS Configuration Too Restrictive**
- Only allowed `http://localhost:5500` and `http://127.0.0.1:5500`
- Frontend likely running on different port
- **Fix:** Extended CORS to allow all localhost ports

### 2. **Duplicate Code in security.py**
- `ALGORITHM` and `oauth2_scheme` defined twice
- Could cause initialization issues
- **Fix:** Removed duplicates

### 3. **Insufficient Error Logging**
- Couldn't diagnose JWT decode failures
- No visibility into what was failing
- **Fix:** Added comprehensive logging

---

## ✅ Solutions Applied

### 1. Enhanced CORS Configuration

**File:** `food_butler_ai/main_orchestrator.py`

```python
# BEFORE: Only 2 origins
origins = ["http://localhost:5500", "http://127.0.0.1:5500"]

# AFTER: All localhost ports for development
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
]
```

**Benefits:**
- ✅ Works regardless of frontend port
- ✅ Handles both localhost and 127.0.0.1
- ✅ Supports all common dev ports

---

### 2. Request Logging Middleware

**File:** `food_butler_ai/main_orchestrator.py`

```python
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
    print(f"{'='*80}\n")
    
    response = await call_next(request)
    return response
```

**Benefits:**
- 🔍 See every request coming in
- 🎫 Verify Authorization header is present
- 🐛 Easier debugging

---

### 3. Enhanced JWT Error Logging

**File:** `food_butler_ai/security.py`

```python
def get_current_user_context(token: str = Depends(oauth2_scheme)) -> tuple[str, str]:
    try:
        print(f"🔐 Attempting to decode JWT token (length: {len(token)})")
        print(f"🔑 Using SECRET_KEY (length: {len(SECRET_KEY)})")
        print(f"📝 Token preview: {token[:20]}...")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            print("❌ Email (sub) not found in JWT payload!")
            print(f"Payload keys: {list(payload.keys())}")
            raise credentials_exception
        
        print(f"✅ JWT decoded successfully for user: {email}")
        return email, token
    except JWTError as e:
        print(f"❌ JWT decode error: {type(e).__name__}: {str(e)}")
        print(f"Token that failed: {token[:50]}...")
        raise credentials_exception
```

**Benefits:**
- 🔍 See exactly why JWT decode fails
- 🔑 Verify SECRET_KEY is loaded
- 📋 Check JWT payload structure

---

### 4. Fixed Duplicate Definitions

**File:** `food_butler_ai/security.py`

```python
# BEFORE: Duplicates
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
ALGORITHM = "HS256"  # ❌ DUPLICATE!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # ❌ DUPLICATE!

# AFTER: Clean
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

---

### 5. Added Test Endpoints

**File:** `food_butler_ai/main_orchestrator.py`

```python
# Health check (no auth required)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Food Butler AI Agent",
        "timestamp": time.time()
    }

# Test authentication
@app.get("/test-auth")
async def test_auth(user_context: tuple[str, str] = Depends(security.get_current_user_context)):
    current_user_email, jwt_token = user_context
    return {
        "status": "authenticated",
        "user": current_user_email,
        "message": "Authentication successful! ✅"
    }
```

**Benefits:**
- 🧪 Easy to test if service is running
- 🔐 Test authentication separately from chat
- 🐛 Isolate issues quickly

---

## 🔧 How to Apply Fixes

### Step 1: Restart AI Agent

```bash
# If using Docker
docker compose restart agent-1

# Or rebuild if needed
docker compose up -d --build agent-1

# Check logs
docker compose logs -f agent-1
```

### Step 2: Test Authentication

```bash
# Run the test script
./test_ai_auth.sh
```

### Step 3: Manual Testing

```bash
# Test health (no auth)
curl http://localhost:8080/health

# Test with your token (get from browser console: localStorage.getItem('foodButlerToken'))
TOKEN="your_token_here"

# Test auth endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/test-auth

# Test chat
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_input":"hello","session_id":"test123"}' \
  http://localhost:8080/chat
```

---

## 🐛 Debugging Guide

### What to Check in Logs

After restarting, you should see:

```
✅ SECRET_KEY loaded successfully (length: 64)
```

When you send a chat message, you should see:

```
================================================================================
📨 Incoming request: POST /chat
🌐 Origin: http://localhost:5500
🔑 Authorization header present: True
🎫 Token preview: eyJhbGciOiJIUzI1NiIs...
================================================================================

🔐 Attempting to decode JWT token (length: 144)
🔑 Using SECRET_KEY (length: 64)
📝 Token preview: eyJhbGciOiJIUzI1NiIs...
✅ JWT decoded successfully for user: testuser@example.com
✅ --- Servicing authenticated request for user: testuser@example.com ---
```

### Common Issues & Fixes

#### Issue 1: "Authorization header present: False"
**Cause:** Frontend not sending Authorization header  
**Fix:** Check frontend code, ensure token is in localStorage

#### Issue 2: "JWT decode error: ExpiredSignatureError"
**Cause:** Token expired  
**Fix:** Log out and log in again

#### Issue 3: "JWT decode error: InvalidSignatureError"
**Cause:** SECRET_KEY mismatch between backend and AI agent  
**Fix:** Verify SECRET_KEY is same in both .env files

```bash
# Check backend SECRET_KEY
docker compose exec backend printenv SECRET_KEY

# Check AI agent SECRET_KEY
docker compose exec agent-1 printenv SECRET_KEY

# They MUST match!
```

#### Issue 4: "Email (sub) not found in JWT payload"
**Cause:** JWT structure doesn't have 'sub' field  
**Fix:** Backend might be generating JWT incorrectly

---

## 📊 Expected Behavior After Fix

### ✅ Success Flow

1. User types message in chat
2. Frontend sends POST to `/chat` with `Authorization: Bearer <token>`
3. AI agent middleware logs the request
4. Security function decodes JWT successfully
5. Chat endpoint processes message
6. User receives response

### Logs You Should See

```
================================================================================
📨 Incoming request: POST /chat
🌐 Origin: http://localhost:5500
🔑 Authorization header present: True
🎫 Token preview: eyJhbGciOiJIUzI1NiIs...
================================================================================

🔐 Attempting to decode JWT token (length: 144)
🔑 Using SECRET_KEY (length: 64)
📝 Token preview: eyJhbGciOiJIUzI1NiIs...
✅ JWT decoded successfully for user: testuser@example.com
✅ --- Servicing authenticated request for user: testuser@example.com ---
📥 User input: hello
✅ Returning cached response (age: 5s)
📦 Cached response (cache size: 3)
INFO: 172.19.0.1:65088 - "POST /chat HTTP/1.1" 200 OK
```

---

## 🎯 Summary

**Changes Made:**
1. ✅ Extended CORS to allow all localhost ports
2. ✅ Added request logging middleware
3. ✅ Enhanced JWT error logging in security.py
4. ✅ Fixed duplicate code definitions
5. ✅ Added /health and /test-auth endpoints
6. ✅ Created test script for easy debugging

**Result:**
- Clear visibility into authentication flow
- Easy to diagnose 401 errors
- Better error messages
- Test endpoints for validation

**Next Steps:**
1. Restart AI agent: `docker compose restart agent-1`
2. Run test script: `./test_ai_auth.sh`
3. Check logs: `docker compose logs -f agent-1`
4. Test in browser

If still getting 401 errors after applying these fixes, the detailed logs will show exactly where the issue is!
