import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    host='0.0.0.0'
    port=4000
    uvicorn.run("app.main:app", host= host, port= port, reload=True)
