# Restaurant Management Page Guide

## Overview
The Restaurant Management page (`restaurant_management.html`) allows restaurant admins to manage their menu items and orders.

## How to Access

### Method 1: Direct Login (Recommended for Restaurant Admins)
1. Open: `http://localhost:5500/frontend/restaurant_management.html`
2. Login with restaurant admin credentials
3. The page will automatically detect your restaurant from the authentication token

### Method 2: Create a Restaurant Admin Account
1. Login to Super Admin dashboard (`admin.html`)
2. Create a restaurant with admin credentials:
   - Restaurant Admin Email: `manager@restaurant.com`
   - Restaurant Admin Password: `manager123`
3. Then login to restaurant_management.html with those credentials

## Features

### 📦 Orders Tab
- View all orders containing items from your restaurant
- Update order status (Pending, Confirmed, Preparing, Completed, Cancelled)
- See customer details and order items
- Track total revenue, pending orders, and completed orders

### 🍽️ Menu Items Tab
- Add new menu items with:
  - Name, Description, Price
  - Availability toggle
- Edit existing menu items
- Delete menu items
- Toggle item availability on/off

### 📊 Analytics Tab
- View most popular menu item
- Average order value
- Total menu items count
- Available items count

## API Endpoints Used

### Authentication
- `POST /restaurant-admin/token` - Restaurant admin login

### Restaurants
- `GET /restaurants/{restaurant_id}` - Get restaurant details
- `GET /restaurants/{restaurant_id}/menu` - Get restaurant menu items

### Menu Items
- `POST /admin/menu-items/` - Add new menu item
- `PUT /admin/menu-items/{id}` - Update menu item
- `DELETE /admin/menu-items/{id}` - Delete menu item

### Orders
- `GET /admin/orders` - Get all orders (filtered for restaurant)
- `PUT /admin/orders/{id}/status` - Update order status

## Key Fixes Applied

1. ✅ **Authentication Fixed**: Now uses `/restaurant-admin/token` endpoint
2. ✅ **Token Decoding**: Automatically extracts restaurant_id from JWT token
3. ✅ **Correct API Endpoints**: Updated to use proper admin endpoints
4. ✅ **Menu Items Loading**: Now correctly fetches from `/restaurants/{id}/menu`
5. ✅ **Add/Update/Delete**: All menu operations use admin endpoints
6. ✅ **LocalStorage Persistence**: Restaurant ID saved for session continuity

## Testing the Page

### Step 1: Create Test Restaurant Admin
Run this in browser console on admin.html:
```javascript
// After logging in as super admin
fetch('http://localhost:8000/restaurants/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('foodButlerToken')}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: "Test Restaurant",
        cuisine: "Multi-cuisine",
        location: "Test Location",
        address: "123 Test Street",
        restaurant_admin_email: "test@restaurant.com",
        restaurant_admin_password: "test123"
    })
}).then(r => r.json()).then(console.log);
```

### Step 2: Login to Restaurant Management
1. Open `http://localhost:5500/frontend/restaurant_management.html`
2. Login with:
   - Email: `test@restaurant.com`
   - Password: `test123`

### Step 3: Add Menu Items
1. Click "Add New Menu Item" button
2. Fill in the form:
   - Name: "Test Burger"
   - Description: "Delicious burger"
   - Price: 250
   - Check "Available"
3. Submit

### Step 4: Verify in Other Pages
1. Check admin.html - Should see the new menu item
2. Check index.html - After login, browse restaurants and see the new item

## Troubleshooting

### Issue: "No restaurant assigned" error
**Solution**: Make sure you're logging in with restaurant admin credentials (not regular customer credentials)

### Issue: Menu items not showing
**Solution**: 
1. Check if restaurant has menu items in admin.html
2. Make sure items are marked as "available"
3. Check browser console for errors

### Issue: Can't add menu items
**Solution**:
1. Check if backend is running on port 8000
2. Verify restaurant admin token is valid
3. Check network tab for API errors

### Issue: Orders not filtering correctly
**Solution**: Orders are filtered by restaurant_id - make sure the order contains items from your restaurant

## Integration with Other Pages

### With admin.html (Super Admin)
- Super admin can see all restaurants and their menu items
- Super admin can edit any restaurant's details
- Changes made in restaurant_management.html appear in admin.html

### With index.html (Customer App)
- Menu items added via restaurant_management.html appear in customer menu
- Availability toggles control what customers can order
- Order status updates reflect in customer order history

## Next Steps

1. **Enhanced Edit Modal**: Currently shows alert, needs full edit form
2. **Order Details Modal**: Add detailed view for each order
3. **Image Upload**: Implement image upload for menu items
4. **Inventory Management**: Add stock tracking for menu items
5. **Real-time Updates**: Use WebSockets for live order notifications

## Security Notes

- Restaurant admins can ONLY see orders containing their items
- Restaurant admins can ONLY manage their own menu items
- JWT token contains restaurant_id for authorization
- Token expires after 30 minutes (default)
