from typing import Callable

from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi_pagination import add_pagination

from app.auth.dependencies import oauth2_scheme
from app.config.settings import settings
from app.database import Base, engine
from app.errors import AppError
from app.routers import airport_codes, balances, flight_sessions, itinerary_types, payment_types, plane_status, planes, roles, transactions, users


def use_route_names_as_operation_ids(route: APIRoute) -> str:
    """Generate unique OpenAPI operation IDs from route function names."""
    return route.name


tags_metadata = [
    {
        "name": "users",
        "description": "User management: registration, login, profile, CRUD.",
    },
    {
        "name": "roles",
        "description": "Role management: list, assign, revoke roles.",
    },
    {
        "name": "balances",
        "description": "Account balances: list, view by user, view own.",
    },
    {
        "name": "transactions",
        "description": "Financial transactions: list, view by user, create debits/credits.",
    },
    {
        "name": "planes",
        "description": "Aircraft management: CRUD plane records and status.",
    },
    {
        "name": "flight_sessions",
        "description": "Flight session management: create sessions with billing, list sessions.",
    },
    {
        "name": "airport_codes",
        "description": "Airport code lookup data.",
    },
    {
        "name": "payment_types",
        "description": "Payment type lookup data.",
    },
    {
        "name": "itinerary_types",
        "description": "Itinerary type lookup data.",
    },
    {
        "name": "plane_status",
        "description": "Plane status lookup data.",
    },
]

app = FastAPI(
    title="AeroClub REST API",
    description="RESTful API for managing aviation training center operations: user authentication, role-based access control, financial ledger accounting, and flight session billing.",
    version="2.0.0",
    openapi_tags=tags_metadata,
    generate_unique_id_function=use_route_names_as_operation_ids,
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
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


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

add_pagination(app)


@app.get("/", tags=["root"])
def root():
    return {"msg": "AeroClub REST API", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
