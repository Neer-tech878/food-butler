# 🍽️ Restaurant Management Page - Quick Start Guide

## Step-by-Step Setup

### Option 1: Automated Setup (Recommended) ⚡

```bash
# Make sure backend is running
cd food_butler_backend
uvicorn app.main:app --reload

# In a new terminal, run setup script
cd /Users/jaswanthyamana/food_butler_platform
./setup_restaurant.sh
```

**The script will:**
1. ✅ Verify backend is running
2. ✅ Login as super admin
3. ✅ Create a test restaurant
4. ✅ Add 5 sample menu items
5. ✅ Provide login credentials

**Then simply:**
- Open: `http://localhost:5500/frontend/restaurant_management.html`
- Login with the provided credentials
- Start managing!

---

### Option 2: Manual Setup 🔧

#### 1. Create Restaurant Admin via Admin Dashboard

**Navigate to:**
```
http://localhost:5500/frontend/admin.html
```

**Login:**
- Email: `admin@foodbutler.com`
- Password: `admin123`

**Create Restaurant:**
1. Click "Restaurant Management" tab
2. Scroll to "Add New Restaurant"
3. Fill in:
   ```
   Name: My Restaurant
   Cuisine: Italian
   Location: Downtown
   Restaurant Admin Email: chef@myrestaurant.com
   Restaurant Admin Password: chef123
   ```
4. Click "Add Restaurant"

#### 2. Access Restaurant Management

**Navigate to:**
```
http://localhost:5500/frontend/restaurant_management.html
```

**Login:**
- Email: `chef@myrestaurant.com`
- Password: `chef123`

#### 3. Add Your First Menu Item

1. Click "🍽️ Menu Items" tab
2. Click "➕ Add New Menu Item"
3. Fill in:
   ```
   Name: Margherita Pizza
   Description: Classic Italian pizza
   Price: 350
   ✓ Available
   ```
4. Click "Add Menu Item"

---

## 🎯 What You Can Do

### Orders Management
- **View** all orders containing your items
- **Update** order status (Pending → Preparing → Completed)
- **Track** revenue and statistics

### Menu Management
- **Add** new dishes to your menu
- **Edit** prices and descriptions
- **Toggle** availability on/off
- **Delete** items permanently

### Analytics
- See your most popular dish
- Track average order value
- Monitor total items and availability

---

## 🔗 Page Integration

### Changes Flow:

```
restaurant_management.html (Add Item)
    ↓
Backend Database (PostgreSQL)
    ↓
admin.html (Super Admin sees it)
    ↓
index.html (Customers can order it)
    ↓
restaurant_management.html (You see the order)
```

**Real-time sync across all pages!**

---

## 🎮 Try These Actions

### Test 1: Add Menu Item
1. Add "Cheese Pizza" - ₹300
2. Open `admin.html` → Check if it appears
3. Open `index.html` → Login → Browse restaurants → See it in menu

### Test 2: Toggle Availability
1. Turn off "Cheese Pizza" availability
2. Refresh `index.html` → Item should disappear from menu
3. Turn it back on → Item reappears

### Test 3: Process Order
1. In `index.html`, order some items
2. In `restaurant_management.html`, see the order appear
3. Change status to "Preparing" → "Completed"
4. In `index.html`, order history shows updated status

---

## 🚨 Troubleshooting

### "No restaurant assigned" Error
**Cause:** Using wrong login credentials
**Fix:** Use restaurant admin email (not customer email)

### Menu Items Not Showing
**Cause:** No items added yet OR all items unavailable
**Fix:** Add items via "Add New Menu Item" button

### Can't Login
**Cause:** Restaurant admin not created
**Fix:** Use admin.html to create restaurant with admin credentials

### Backend Not Responding
**Check:** Is backend running on port 8000?
```bash
curl http://localhost:8000/
# Should return: {"message": "Welcome to the Food Butler Backend API"}
```

---

## 📱 Screenshots Guide

### Login Screen
```
┌─────────────────────────────────┐
│  🏪 Restaurant Admin Login      │
│                                 │
│  ┌───────────────────────────┐ │
│  │ Email                     │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ Password                  │ │
│  └───────────────────────────┘ │
│         [Login Button]          │
└─────────────────────────────────┘
```

### Dashboard
```
┌────────────────────────────────────────────┐
│ 🏪 Restaurant Management    [Logout]      │
│ My Restaurant - Italian • Downtown         │
├────────────────────────────────────────────┤
│ [📦 Orders] [🍽️ Menu] [📊 Analytics]      │
├────────────────────────────────────────────┤
│                                            │
│  Statistics:                               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐     │
│  │  15  │ │   3  │ │  12  │ │ ₹4500│     │
│  │Total │ │Pend. │ │Comp. │ │ Rev. │     │
│  └──────┘ └──────┘ └──────┘ └──────┘     │
│                                            │
│  Menu Items:                               │
│  [➕ Add New Menu Item]                   │
│  ┌────────────────────────────────────┐   │
│  │ Pizza | ₹350 | Available ⚫ ON     │   │
│  │ Pasta | ₹280 | Available ⚫ ON     │   │
│  │ Salad | ₹180 | Available ⚪ OFF    │   │
│  └────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

---

## ✅ Verification Checklist

After setup, verify these work:

- [ ] Can login with restaurant admin credentials
- [ ] Dashboard shows restaurant name
- [ ] Can add a new menu item
- [ ] Menu item appears in list
- [ ] Can toggle item availability
- [ ] Can delete menu item
- [ ] Orders tab loads (may be empty)
- [ ] Analytics tab shows statistics
- [ ] Can logout and login again
- [ ] Menu item appears in customer app (index.html)

---

## 🎓 Pro Tips

1. **Use descriptive names** - Helps customers find items
2. **Set realistic prices** - Matches your restaurant positioning
3. **Toggle off items** instead of deleting when out of stock
4. **Check orders regularly** - Update status promptly
5. **Use descriptions** - Helps customers make decisions

---

## 🆘 Getting Help

**Check logs:**
```bash
# Backend logs
cd food_butler_backend
tail -f backend.log

# Browser console
Press F12 → Console tab
```

**Test backend:**
```bash
# Check if backend is healthy
curl http://localhost:8000/health
```

**Reset and start fresh:**
```bash
# Re-run setup script
./setup_restaurant.sh
```

---

## 🎉 You're All Set!

Your restaurant management page is now fully functional. You can:
- ✅ Manage menu items in real-time
- ✅ Track orders and revenue
- ✅ Update availability instantly
- ✅ See changes across all pages

**Happy Restaurant Managing! 🍽️✨**
