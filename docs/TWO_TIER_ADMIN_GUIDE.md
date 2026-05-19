# Two-Tier Admin System Guide

## Overview

Food Butler now has a **two-tier admin system** to manage the platform:

1. **Super Admin** - Full platform control (create/manage restaurants, view all orders)
2. **Restaurant Admin** - Restaurant-specific management (manage their own menu and orders)

---

## Super Admin

### Access
- **URL**: `http://127.0.0.1:5500/frontend/admin.html`
- **Credentials**: `admin@foodbutler.com` / `admin123`

### Capabilities
- ✅ View and manage all orders across all restaurants
- ✅ Create new restaurants
- ✅ Assign restaurant admin credentials
- ✅ View restaurant overview and statistics
- ✅ Manage restaurant details

### Creating a New Restaurant with Admin Access

1. Login to the Super Admin dashboard
2. Navigate to **Restaurant Management** section
3. Scroll to **Add New Restaurant** form
4. Fill in restaurant details:
   - Restaurant Name
   - Cuisine
   - Location (using map picker)
   - Logo URL
5. **Create Restaurant Admin Access:**
   - Enter **Restaurant Admin Email** (e.g., `manager@pizzahut.com`)
   - Enter **Restaurant Admin Password** (e.g., `secure123`)
6. Click **Add Restaurant**

The restaurant admin can now login with their credentials!

---

## Restaurant Admin

### Access
- **URL**: `http://127.0.0.1:5500/frontend/restaurant_admin.html`
- **Credentials**: Provided by Super Admin during restaurant creation

### Capabilities
- ✅ View orders specific to their restaurant
- ✅ View revenue from their restaurant's orders
- ✅ Manage menu item availability (toggle available/unavailable)
- ✅ View menu item inventory
- ✅ Dashboard with restaurant-specific statistics

### Features

#### Dashboard Statistics
- **Total Orders**: Number of orders containing items from this restaurant
- **Menu Items**: Total number of items in the menu
- **Available Items**: Currently available menu items
- **Total Revenue**: Revenue generated from completed orders

#### Orders Management
- View all orders containing items from their restaurant
- See order details: Customer, Items, Total, Status, Date
- Orders are filtered to show only items from their restaurant

#### Menu Management
- View all menu items
- Toggle availability with a simple switch
- View current stock levels
- See item descriptions and prices

---

## Authentication Flow

### Backend Endpoints

1. **Super Admin Login**
   - Endpoint: `POST /token`
   - Body: `{ "username": "admin@foodbutler.com", "password": "admin123" }`
   - Returns: JWT token with customer authentication

2. **Restaurant Admin Login**
   - Endpoint: `POST /restaurant-admin/token`
   - Body: `{ "username": "manager@restaurant.com", "password": "password" }`
   - Returns: JWT token with restaurant authentication and restaurant_id

### Token Structure

**Super Admin Token Payload:**
```json
{
  "sub": "admin@foodbutler.com",
  "exp": 1234567890
}
```

**Restaurant Admin Token Payload:**
```json
{
  "sub": "manager@restaurant.com",
  "restaurant_id": "uuid-here",
  "user_type": "restaurant_admin",
  "exp": 1234567890
}
```

---

## Database Schema

### Restaurants Table
- `id`: UUID (Primary Key)
- `name`: String
- `cuisine`: String
- `location`: String
- `address`: String
- `logo_url`: String
- `restaurant_admin_email`: String (Unique)
- `restaurant_admin_hashed_password`: String (Bcrypt hashed)

### Key Features
- Restaurant admin credentials are stored securely with bcrypt hashing
- Each restaurant can have one admin account
- Admin email must be unique across the platform

---

## Security Features

1. **Password Hashing**: All passwords (both super admin and restaurant admin) are hashed using bcrypt
2. **JWT Authentication**: Secure token-based authentication
3. **Role-Based Access**: Restaurant admins can only access their own restaurant data
4. **Token Expiration**: Tokens expire after a set period for security

---

## Example Workflow

### Scenario: Adding a New Pizza Restaurant

1. **Super Admin** logs in at `admin.html`
2. Goes to **Restaurant Management** → **Add New Restaurant**
3. Fills in:
   ```
   Name: Mario's Pizza
   Cuisine: Italian
   Location: (select on map)
   Logo URL: https://example.com/logo.png
   Admin Email: mario@mariospizza.com
   Admin Password: pizza2024
   ```
4. Clicks **Add Restaurant**
5. Restaurant is created with hashed password

6. **Restaurant Manager (Mario)** receives credentials
7. Goes to `restaurant_admin.html`
8. Logs in with:
   ```
   Email: mario@mariospizza.com
   Password: pizza2024
   ```
9. Sees dashboard with:
   - Current orders for Mario's Pizza
   - Menu items for Mario's Pizza
   - Revenue statistics
   - Can toggle menu availability

---

## API Endpoints Reference

### Super Admin Endpoints
- `POST /token` - Super admin login
- `GET /admin/orders` - Get all orders
- `POST /admin/restaurants` - Create restaurant (with admin credentials)
- `GET /restaurants/` - List all restaurants
- `GET /restaurants/{id}` - Get restaurant details

### Restaurant Admin Endpoints
- `POST /restaurant-admin/token` - Restaurant admin login
- `GET /admin/orders` - Get all orders (filtered by restaurant on frontend)
- `GET /restaurants/{id}/menu` - Get restaurant menu items
- `PUT /admin/menu-items/{id}` - Update menu item availability

---

## Troubleshooting

### Restaurant Admin Can't Login
- ✅ Check that restaurant was created with admin credentials
- ✅ Verify email and password are correct
- ✅ Check backend logs for authentication errors
- ✅ Ensure backend is running: `docker compose ps`

### Restaurant Admin Sees No Orders
- ✅ Check that orders contain items from their restaurant
- ✅ Verify restaurant_id in token matches restaurant
- ✅ Check backend logs for filtering issues

### Menu Item Toggle Not Working
- ✅ Check authentication token is valid
- ✅ Verify menu item belongs to the restaurant
- ✅ Check backend logs for update errors

---

## Future Enhancements

Potential improvements for the restaurant admin system:

1. **Order Status Updates**: Allow restaurant admins to update order status
2. **Menu Item Management**: Add/edit/delete menu items directly
3. **Inventory Management**: Update stock levels
4. **Analytics Dashboard**: Charts and graphs for sales trends
5. **Notification System**: Real-time alerts for new orders
6. **Multi-Restaurant Support**: One admin managing multiple restaurants
7. **Staff Management**: Add multiple admin users per restaurant
8. **Custom Branding**: Restaurant-specific themes and logos

---

## Support

For issues or questions:
- Check backend logs: `docker compose logs backend -f`
- Check database: Connect to PostgreSQL and inspect tables
- Verify API endpoints with curl or Postman
- Review browser console for frontend errors

---

*Last Updated: October 2025*
