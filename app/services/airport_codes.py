from typing import Optional

from app.repositories import AirportCodeRepository
from app.schemas import AirportCodesCreate, AirportCodesOut, AirportCodesUpdate
from ..errors import AirportCodeAlreadyExists, AirportCodeNotFound


def get_airport_codes_srv(db, skip: int = 0, limit: int = 100):
    repo = AirportCodeRepository(db)
    return repo.get_all(skip=skip, limit=limit)


def get_airport_code_by_code_srv(db, code: str) -> AirportCodesOut:
    repo = AirportCodeRepository(db)
    code_obj = repo.get_by_code(code=code)
    if not code_obj:
        raise AirportCodeNotFound
    return AirportCodesOut.model_validate(code_obj)


def create_airport_code_srv(db, code_data: AirportCodesCreate) -> AirportCodesOut:
    repo = AirportCodeRepository(db)
    from app.models import AirportCodes
    airport_code = AirportCodes(**code_data.model_dump())
    try:
        repo.add(airport_code)
    except IntegrityError:
        repo.db.rollback()
        raise AirportCodeAlreadyExists
    return AirportCodesOut.model_validate(airport_code)


def update_airport_code_srv(db, code: str, code_data: AirportCodesUpdate) -> AirportCodesOut:
    repo = AirportCodeRepository(db)
    airport_code = repo.get_by_code(code=code)
    if not airport_code:
        raise AirportCodeNotFound
    try:
        for key, value in code_data.model_dump(exclude_unset=True).items():
            if hasattr(airport_code, key):
                setattr(airport_code, key, value)
        repo.update(airport_code)
    except IntegrityError:
        repo.db.rollback()
        raise AirportCodeAlreadyExists
    return AirportCodesOut.model_validate(airport_code)
