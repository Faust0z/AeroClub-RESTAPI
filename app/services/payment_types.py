from typing import Optional

from sqlalchemy.exc import IntegrityError
from typing import Optional

from app.repositories import PaymentTypeRepository
from app.schemas import PaymentTypesCreate, PaymentTypesOut, PaymentTypesUpdate
from ..errors import PaymentTypeAlreadyExists, PaymentTypeNotFound


def get_payment_types_srv(db, skip: int = 0, limit: int = 100) -> list[PaymentTypesOut]:
    repo = PaymentTypeRepository(db)
    return repo.get_all(skip=skip, limit=limit)


def get_payment_type_by_name_srv(db, name: str) -> PaymentTypesOut:
    repo = PaymentTypeRepository(db)
    pt = repo.get_by_name(name=name)
    if not pt:
        raise PaymentTypeNotFound
    return PaymentTypesOut.model_validate(pt)


def create_payment_type_srv(db, pt_data: PaymentTypesCreate) -> PaymentTypesOut:
    repo = PaymentTypeRepository(db)
    from app.models import PaymentTypes
    payment_type = PaymentTypes(**pt_data.model_dump())
    try:
        repo.add(payment_type)
    except IntegrityError:
        repo.db.rollback()
        raise PaymentTypeAlreadyExists
    return PaymentTypesOut.model_validate(payment_type)


def update_payment_type_srv(db, name: str, pt_data: PaymentTypesUpdate) -> PaymentTypesOut:
    repo = PaymentTypeRepository(db)
    payment_type = repo.get_by_name(name=name)
    if not payment_type:
        raise PaymentTypeNotFound
    try:
        for key, value in pt_data.model_dump(exclude_unset=True).items():
            if hasattr(payment_type, key):
                setattr(payment_type, key, value)
        repo.update(payment_type)
    except IntegrityError:
        repo.db.rollback()
        raise PaymentTypeAlreadyExists
    return PaymentTypesOut.model_validate(payment_type)
