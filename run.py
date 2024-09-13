import os
import uvicorn

if __name__ == "__main__":
    # Prevent Python from generating .pyc files
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    # Use port assigned by Render.com
    port = int(os.environ.get("PORT", 8000))  # Default to 8000 if not set
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
