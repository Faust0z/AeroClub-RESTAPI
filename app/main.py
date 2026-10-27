from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.auth.dependencies import oauth2_scheme
from app.config.settings import settings
from app.database import Base, engine
from app.errors import AppError
from app.routers import airport_codes, balances, flight_sessions, itinerary_types, payment_types, plane_status, planes, roles, transactions, users

app = FastAPI(
    title="AeroClub REST API",
    description="RESTful API for managing aviation training center operations",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return HTTPException(status_code=exc.status_code, detail=exc.detail)


app.include_router(users.router)
app.include_router(roles.router)
app.include_router(balances.router)
app.include_router(transactions.router)
app.include_router(planes.router)
app.include_router(flight_sessions.router)
app.include_router(airport_codes.router)
app.include_router(payment_types.router)
app.include_router(itinerary_types.router)
app.include_router(plane_status.router)


@app.get("/")
def root():
    return {"msg": "AeroClub REST API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
