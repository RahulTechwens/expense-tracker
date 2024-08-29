from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.expense_routes import router as expense_router
import uvicorn
from app.core.config import settings  # Import the settings

app = FastAPI()

# Mount the 'upload' directory
app.mount("/upload", StaticFiles(directory=settings.UPLOAD_DIR), name="upload")

# Include routers
app.include_router(expense_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
