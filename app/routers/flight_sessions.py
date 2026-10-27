from datetime import date
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin, require_admin_or_instructor, require_active_user
from app.database import get_db
from app.errors import BadTimeInput, FlightSessionNotFound, UserNotFound
from app.models import Users
from app.schemas import FlightSessionsCreate, FlightSessionsOut
from app.services.flight_sessions import (
    create_flight_session_srv,
    get_flight_session_by_identifier_srv,
    get_flight_sessions_srv,
    get_user_flight_sessions_srv,
)

router = APIRouter(prefix="/v1/flight_sessions", tags=["flight_sessions"])


@router.get("/", response_model=List[FlightSessionsOut])
def list_flight_sessions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin_or_instructor)],
    flight_session_identifier: Optional[int] = Query(None),
    plane_registration: Optional[str] = Query(None),
    admin_email: Optional[str] = Query(None),
    user_first_name: Optional[str] = Query(None),
    user_last_name: Optional[str] = Query(None),
    observations: Optional[str] = Query(None),
    starting_date: Optional[date] = Query(None),
    limit_date: Optional[date] = Query(None),
):
    sessions = get_flight_sessions_srv(
        db=db,
        flight_session_identifier=flight_session_identifier,
        plane_registration=plane_registration,
        admin_email=admin_email,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        observations=observations,
        starting_date=starting_date,
        limit_date=limit_date,
    )
    return sessions


@router.get("/me", response_model=List[FlightSessionsOut])
def get_my_flight_sessions(
    current_user: Annotated[Users, Depends(require_active_user)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        sessions = get_user_flight_sessions_srv(db=db, email=current_user.email)
    except UserNotFound:
        raise HTTPException(status_code=404, detail="No user found with the given email")
    return sessions


@router.get("/{identifier}", response_model=FlightSessionsOut)
def get_flight_session(
    identifier: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_active_user)],
):
    try:
        session = get_flight_session_by_identifier_srv(db=db, flight_session_identifier=identifier)
    except FlightSessionNotFound:
        raise HTTPException(status_code=404, detail="Flight session not found")
    return session


@router.post("/", response_model=FlightSessionsOut, status_code=status.HTTP_201_CREATED)
def create_flight_session(
    session_data: FlightSessionsCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[Users, Depends(require_admin)],
):
    try:
        session = create_flight_session_srv(
            db=db,
            flight_session_data=session_data.model_dump(),
            admin_email=current_user.email,
        )
    except BadTimeInput:
        raise HTTPException(status_code=400, detail="Arrival time is earlier than departure time")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    return session
