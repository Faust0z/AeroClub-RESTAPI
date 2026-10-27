from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..errors import AirportCodeAlreadyExists, AirportCodeNotFound
from ..models import AirportCodes


def get_airport_codes_srv(db: Session) -> list[AirportCodes]:
    return db.scalars(select(AirportCodes)).all()


def get_airport_code_by_code_srv(db: Session, code: str) -> AirportCodes:
    airport_code = db.execute(select(AirportCodes).where(AirportCodes.code == code)).scalar_one_or_none()
    if not airport_code:
        raise AirportCodeNotFound
    return airport_code


def update_airport_code_srv(db: Session, code: str, data: dict) -> AirportCodes:
    airport_code = get_airport_code_by_code_srv(db=db, code=code)
    try:
        for key, value in data.items():
            if hasattr(airport_code, key):
                setattr(airport_code, key, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AirportCodeAlreadyExists

    return airport_code


def create_airport_code_srv(db: Session, code: str, data: dict) -> AirportCodes:
    airport_code = AirportCodes(**data)
    try:
        db.add(airport_code)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise AirportCodeAlreadyExists
    return airport_code
