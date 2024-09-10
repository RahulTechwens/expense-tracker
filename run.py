import os
import uvicorn

if __name__ == "__main__":
    # Prevent Python from generating .pyc files
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
