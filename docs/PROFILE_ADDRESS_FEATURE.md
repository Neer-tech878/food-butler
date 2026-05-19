# Profile-Based Delivery Address with Live Location

## Overview
Users can now save their delivery address with GPS coordinates in their profile, making checkout faster and more accurate. Live location capture is mandatory to ensure precise delivery.

## Features

### 1. **Profile Address Management**
- New section in user profile for managing delivery address
- Address text field for complete address entry
- **Live Location button** - Captures GPS coordinates using browser geolocation
- Visual feedback showing saved address and coordinates
- One-click address saving with validation

### 2. **Live Location Capture**
- **Mandatory** GPS coordinates for accurate delivery
- Real-time location access using HTML5 Geolocation API
- High accuracy mode enabled
- Error handling for permission denied, unavailable location, or timeout
- Visual status indicators (loading, success, error)

### 3. **Smart Checkout**
- If user has saved address: Shows option to use saved address (selected by default)
- If no saved address: Prompts for new address entry
- Can choose between saved address or enter new address for specific order
- Saved address includes GPS coordinates automatically

### 4. **Backend Integration**
- New columns in `customers` table: `delivery_address`, `delivery_lat`, `delivery_lng`
- New API endpoint: `PUT /customers/me/address` - Update user's delivery address
- Enhanced checkout endpoint: Can use saved address or accept new address
- Automatic fallback to saved address if no address provided in checkout

## User Journey

### Setting Up Delivery Address (One-Time Setup)

```
1. User logs in
   ↓
2. Goes to Profile page
   ↓
3. Sees "Delivery Address" section
   ↓
4. Enters complete address in textarea
   ↓
5. Clicks "Get Live Location (Required)" button
   ├─→ Browser requests location permission
   ├─→ User grants permission
   └─→ GPS coordinates captured ✓
   ↓
6. Status shows: "✓ Location captured: 12.345678, 78.901234"
   ↓
7. Clicks "Save Address"
   ↓
8. Address saved with GPS coordinates ✓
   ↓
9. Confirmation: "✓ Address saved successfully!"
```

### Fast Checkout with Saved Address

```
1. User adds items to cart
   ↓
2. Clicks "Proceed to Checkout"
   ↓
3. Modal shows:
   ┌─────────────────────────────────────┐
   │ ● Use My Saved Address (Selected)  │
   │   123 Main Street, Bangalore       │
   │   📍 12.345678, 78.901234          │
   │                                     │
   │ ○ Enter New Address                 │
   │   [Disabled textarea]               │
   └─────────────────────────────────────┘
   ↓
4. Clicks "Confirm & Checkout"
   ↓
5. Order created with saved address + coordinates ✓
```

### Alternative: Use New Address for Specific Order

```
3. Modal shows saved address option
   ↓
4. User selects "Enter New Address"
   ↓
5. Textarea becomes enabled
   ↓
6. User enters different address
   ↓
7. Clicks "Confirm & Checkout"
   ↓
8. Order created with new address (but profile address unchanged)
```

## Technical Implementation

### Database Schema

```sql
-- customers table (new columns)
ALTER TABLE customers ADD COLUMN delivery_address TEXT NULL;
ALTER TABLE customers ADD COLUMN delivery_lat NUMERIC(10, 7) NULL;
ALTER TABLE customers ADD COLUMN delivery_lng NUMERIC(10, 7) NULL;
```

### API Endpoints

#### Update Customer Address
```
PUT /customers/me/address
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "delivery_address": "123 Main St, Bangalore, Karnataka 560001",
  "delivery_lat": 12.9715987,
  "delivery_lng": 77.5945627
}

Response: 200 OK
{
  "id": "uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "delivery_address": "123 Main St, Bangalore, Karnataka 560001",
  "delivery_lat": 12.9715987,
  "delivery_lng": 77.5945627,
  ...
}
```

#### Enhanced Checkout
```
POST /cart/checkout
Authorization: Bearer <token>
Content-Type: application/json

Body (Option 1 - Use saved address):
{
  "use_saved_address": true
}

Body (Option 2 - Provide new address):
{
  "delivery_address": "456 Park Ave, Delhi 110001",
  "delivery_lat": 28.6139,
  "delivery_lng": 77.2090
}

Body (Option 3 - Empty falls back to saved):
{}
```

### Frontend Components

#### Profile Address Section
- Located in Profile page
- Shows current saved address with coordinates
- Live location button with geolocation API
- Form validation (address required, coordinates required)
- Visual status indicators

#### Checkout Modal Enhancement
- Radio button selection: Saved vs New address
- Dynamic enabling/disabling of new address textarea
- Shows saved address details if available
- Falls back to new address if no saved address

### Geolocation API Usage

```javascript
navigator.geolocation.getCurrentPosition(
    successCallback,
    errorCallback,
    {
        enableHighAccuracy: true,  // Use GPS, not just network
        timeout: 10000,             // 10 second timeout
        maximumAge: 0               // Don't use cached position
    }
);
```

## User Interface

### Profile Page - Address Section

```
┌─────────────────────────────────────────────────────────┐
│  📍 Delivery Address                                    │
│  Your saved address will be used for all deliveries    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ 123 Main Street, Apartment 4B                  │    │
│  │ Koramangala, Bangalore, Karnataka              │    │
│  │ 560034                                          │    │
│  │ 📍 Location: 12.934533, 77.626579              │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ Enter your complete delivery address           │    │
│  │                                                 │    │
│  │                                                 │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  [ 📍 Get Live Location (Required) ]  ✓ Location saved │
│                                                          │
│  [          Save Address          ]                     │
└─────────────────────────────────────────────────────────┘
```

### Checkout Modal - With Saved Address

```
┌─────────────────────────────────────────────────────────┐
│  📍 Delivery Address                                    │
│  Choose delivery address for this order.               │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ ● Use My Saved Address                         │    │
│  │   123 Main Street, Apartment 4B                │    │
│  │   Koramangala, Bangalore, Karnataka 560034     │    │
│  │   📍 12.934533, 77.626579                      │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │ ○ Enter New Address                            │    │
│  │   [Enter your complete delivery address...]    │    │
│  │   (Disabled)                                    │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│                    [ Cancel ] [ Confirm & Checkout ]    │
└─────────────────────────────────────────────────────────┘
```

## Benefits

### For Users
✅ **Faster Checkout** - No need to enter address every time
✅ **Accurate Delivery** - GPS coordinates ensure precise location
✅ **Easy Setup** - One-time address saving in profile
✅ **Flexible** - Can use saved or enter new address per order
✅ **Visual Feedback** - See saved address and coordinates
✅ **Mobile Friendly** - Works with smartphone GPS

### For Business
✅ **Better Data Quality** - All addresses have GPS coordinates
✅ **Reduced Errors** - Accurate coordinates prevent wrong deliveries
✅ **Faster Deliveries** - Drivers can navigate directly to coordinates
✅ **User Retention** - Convenient saved address encourages repeat orders
✅ **Analytics** - Can analyze delivery patterns by location

### For Drivers
✅ **Easy Navigation** - GPS coordinates work with any navigation app
✅ **Fewer Calls** - Accurate location reduces need to call customers
✅ **Faster Deliveries** - Direct navigation to exact location

## Validation & Error Handling

### Address Validation
- Address text is required (cannot be empty)
- GPS coordinates are required (must click "Get Live Location")
- Frontend validates before API call
- Backend validates in Pydantic schema

### Geolocation Errors

| Error | Cause | Solution |
|-------|-------|----------|
| PERMISSION_DENIED | User denied location access | Show instructions to enable in browser settings |
| POSITION_UNAVAILABLE | GPS unavailable | Ask user to check device settings |
| TIMEOUT | Request took too long | Try again or check GPS signal |
| Not Supported | Browser doesn't support geolocation | Use desktop/modern mobile browser |

### User Feedback

```javascript
// Loading
"Getting location..."  (Blue)

// Success
"✓ Location captured: 12.345678, 78.901234"  (Green)

// Error
"✗ Location access denied"  (Red)
"✗ Geolocation not supported"  (Red)
```

## Migration

```bash
# Run the migration
docker compose exec backend alembic upgrade head

# This will:
# - Add delivery_address column to customers table
# - Add delivery_lat column to customers table  
# - Add delivery_lng column to customers table
```

## Testing

### Test Address Saving
1. Login to app
2. Go to Profile
3. Enter address: "123 Test Street, Bangalore 560001"
4. Click "Get Live Location" → Grant permission
5. Verify coordinates appear
6. Click "Save Address"
7. Verify success message
8. Refresh page → Address should still be saved

### Test Fast Checkout
1. With saved address, add items to cart
2. Click "Proceed to Checkout"
3. Verify saved address is pre-selected
4. Click "Confirm & Checkout"
5. Verify order created successfully

### Test New Address in Checkout
1. With saved address, go to checkout
2. Select "Enter New Address"
3. Enter different address
4. Click "Confirm & Checkout"
5. Verify order uses new address
6. Go to Profile → Verify saved address unchanged

### Test No Saved Address
1. New user without saved address
2. Add items and checkout
3. Verify only "Enter New Address" option shown
4. Must enter address to proceed

## Security Considerations

✅ **Location Permission** - Browser asks user permission before accessing GPS
✅ **User Control** - Users can deny location access (but then can't save address)
✅ **No Tracking** - Location only captured when user clicks button, not continuous
✅ **HTTPS Required** - Geolocation API only works on secure connections
✅ **Privacy** - Coordinates stored only for delivery purposes

## Browser Compatibility

| Browser | Geolocation Support |
|---------|-------------------|
| Chrome 50+ | ✅ Yes |
| Firefox 55+ | ✅ Yes |
| Safari 14+ | ✅ Yes |
| Edge 79+ | ✅ Yes |
| Mobile Safari | ✅ Yes |
| Mobile Chrome | ✅ Yes |

## Future Enhancements

🔮 **Multiple Addresses** - Save home, work, etc.
🔮 **Address Labels** - Name addresses (Home, Office, etc.)
🔮 **Address Book** - Manage multiple saved addresses
🔮 **Recent Addresses** - Show recently used addresses
🔮 **Map Preview** - Show pin on map when saving address
🔮 **Address Autocomplete** - Google Places API integration
🔮 **Edit Coordinates** - Manually adjust pin on map

## Summary

This feature transforms the checkout experience by:
- Making delivery addresses easy to manage
- Ensuring accurate GPS coordinates for every delivery
- Speeding up checkout for returning customers
- Reducing delivery errors with precise location data

All with a beautiful, user-friendly interface! 🎉
