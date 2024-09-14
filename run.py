import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    host=os.getenv("HOST")
    port=int(os.getenv("PORT"))
    uvicorn.run("app.main:app", host= host, port= port, reload=True)
