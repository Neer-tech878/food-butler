from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Corrected imports to be relative from the 'app' package
from .routers import menu, orders, customers, auth, payments, cart, inventory, admin, restaurants, delivery

app = FastAPI(
    title="Food Butler Backend",
    description="The backend service for the Food Butler application and AI Agent.",
    version="1.0.0",
)

# CORS Middleware Configuration
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5502",
    "http://127.0.0.1:5502",
    "http://localhost:5503",
    "http://127.0.0.1:5503",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://127.0.0.1",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all the routers in the application
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(menu.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(inventory.router)
app.include_router(admin.router)
app.include_router(restaurants.router)
app.include_router(delivery.router)


@app.get("/", tags=["Root"])
async def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the Food Butler Backend API"}

