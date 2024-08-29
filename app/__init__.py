from fastapi import FastAPI # type: ignore
from app.routes.expense_routes import router as expense_router
from app.db.connection import mongodb
app = FastAPI()
app.include_router(expense_router)
@app.on_event("startup")
async def startup_db_client():
    await mongodb.get_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    mongodb.client.close()
