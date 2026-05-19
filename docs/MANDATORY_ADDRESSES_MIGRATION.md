# Making Addresses Mandatory - Migration Guide

## Overview
This update makes delivery addresses mandatory for both restaurants and orders to ensure proper delivery tracking functionality.

## Changes Made

### 1. Database Schema (models.py)
- **Restaurant.location**: Changed from nullable to `nullable=False` (mandatory)
- **Order.delivery_address**: Changed from nullable to `nullable=False` (mandatory)

### 2. API Schemas (schemas.py)
- **RestaurantBase.location**: Changed from `Optional[str]` to `str` (required)
- **OrderCreate.delivery_address**: Changed from `Optional[str]` to `str` (required)

### 3. Backend API (routers/cart.py)
- Added `CheckoutRequest` schema with mandatory `delivery_address` field
- Updated `/cart/checkout` endpoint to require delivery address in request body

### 4. Frontend Changes

#### Admin Panel (admin.html)
- Restaurant location field now has `required` attribute
- Placeholder updated to: "Full Address (Required for delivery)"
- Both add and edit forms enforce address requirement

#### Customer UI (index.html)
- Added delivery address modal that appears before checkout
- Modal includes:
  - Large textarea for complete address
  - Required validation
  - Cancel and Confirm buttons
- Checkout button now triggers modal instead of direct checkout
- API updated to send delivery_address in POST body

## Migration Steps

### Step 1: Run the Database Migration

The migration will:
1. Set default value "Address not provided" for existing NULL locations/addresses
2. Make the columns NOT NULL

Run this command in your Docker terminal:

```bash
docker compose exec backend alembic upgrade head
```

Or if you get the docker terminal separately:
```bash
# Get into the backend container
docker compose exec backend bash

# Run migration
alembic upgrade head

# Exit
exit
```

### Step 2: Verify Migration

Check that the migration was applied:
```bash
docker compose exec backend alembic current
```

You should see: `make_addresses_mandatory`

### Step 3: Update Existing Data (if needed)

If you have existing restaurants or orders with placeholder addresses, update them:

```sql
-- Connect to database
docker compose exec db psql -U postgres -d food_butler

-- Update restaurant locations
UPDATE restaurants SET location = 'Actual address here' WHERE location = 'Address not provided';

-- Update order delivery addresses
UPDATE orders SET delivery_address = 'Customer address' WHERE delivery_address = 'Address not provided';
```

### Step 4: Restart Services

```bash
docker compose down
docker compose up -d
```

### Step 5: Test the Changes

1. **Test Restaurant Creation:**
   - Go to Admin Panel
   - Try to create restaurant without location → Should fail validation
   - Create restaurant with location → Should succeed

2. **Test Order Checkout:**
   - Add items to cart
   - Click "Proceed to Checkout"
   - Modal should appear requesting delivery address
   - Try to submit empty address → Should show validation error
   - Enter address and submit → Order should be created with address

3. **Test Delivery Tracking:**
   - Go to "Track Order" page
   - Select an order
   - Map should show centered on India
   - If order has coordinates, map should zoom to show delivery location

## API Changes

### New Request Format for Checkout

**Before:**
```json
POST /cart/checkout
Headers: Authorization: Bearer <token>
Body: (empty or optional delivery_info)
```

**After:**
```json
POST /cart/checkout
Headers: 
  Authorization: Bearer <token>
  Content-Type: application/json
Body: {
  "delivery_address": "123 Main St, City, State 12345",
  "delivery_lat": 20.5937,  // optional
  "delivery_lng": 78.9629   // optional
}
```

## Validation Rules

### Restaurant Location
- **Required**: Yes
- **Type**: String
- **Min Length**: No limit (but should be meaningful address)
- **Example**: "123 MG Road, Bangalore, Karnataka 560001"

### Order Delivery Address
- **Required**: Yes
- **Type**: String (Text in database)
- **Min Length**: No limit (but should be complete address)
- **Example**: "Flat 201, Building A, Green Park, Sector 15, Delhi 110001"

## Troubleshooting

### Error: "null value in column 'location' violates not-null constraint"
- This means migration wasn't run or failed
- Run: `docker compose exec backend alembic upgrade head`

### Error: "Field required" when creating restaurant
- This is expected! Location is now mandatory
- Enter a valid address in the Location field

### Error: Checkout fails with "Field required"
- This is expected! Delivery address is now mandatory
- The modal should appear automatically - enter your address

### Modal doesn't appear on checkout
- Hard refresh browser (Cmd + Shift + R)
- Clear browser cache
- Check browser console for errors

## Rollback (if needed)

If you need to revert these changes:

```bash
docker compose exec backend alembic downgrade -1
```

This will make the fields nullable again.

## Benefits

✅ **Better Delivery Tracking**: Every order now has a delivery address
✅ **Accurate Maps**: Restaurant locations ensure proper map visualization
✅ **Data Quality**: No orders or restaurants without location information
✅ **User Experience**: Clear modal prompts users for required information
✅ **Validation**: Both frontend and backend enforce address requirements

