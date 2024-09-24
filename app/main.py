from fastapi import FastAPI # type: ignore
from app.routes.expense_routes import router as expense_router
from app.routes.alert_routes import router as alert_router
from app.routes.parse_sms_routes import router as parse_sms_router
from app.routes.goals_routes import router as goals_router
from app.routes.auth_routes import router as auth_router
import uvicorn # type: ignore
from app.core.config import settings

app = FastAPI()


app.include_router(expense_router, prefix="/api", tags=["Expenses"])
app.include_router(alert_router, prefix="/api", tags=["Alerts"])
app.include_router(parse_sms_router, prefix="/api", tags=["ParseSms"])
app.include_router(goals_router, prefix="/api", tags=["Goals"])
app.include_router(auth_router, prefix="/api", tags=["Authentication"])



if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
