from fastapi import APIRouter

# This router is a placeholder for our future payment integration.
# It needs to exist so app.main can import it without errors.

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    responses={404: {"description": "Not found"}},
)

# We will add endpoints like /create-payment-intent here later.
