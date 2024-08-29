# app/__init__.py

from fastapi import FastAPI
from app.routes.expense_routes import router as expense_router
from app.db.connection import mongodb

# Create the FastAPI app instance
app = FastAPI()

# Include the router
app.include_router(expense_router)

# Optionally, you can add startup/shutdown events
@app.on_event("startup")
async def startup_db_client():
    await mongodb.get_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    mongodb.client.close()
