from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..errors import PaymentTypeAlreadyExists, PaymentTypeNotFound
from ..models import PaymentTypes


def get_payment_types_srv(db: Session) -> list[PaymentTypes]:
    return db.scalars(select(PaymentTypes)).all()


def get_payment_type_by_name_srv(db: Session, name: str) -> PaymentTypes:
    payment_type = db.execute(select(PaymentTypes).where(PaymentTypes.type == name)).scalar_one_or_none()
    if not payment_type:
        raise PaymentTypeNotFound
    return payment_type


def update_payment_type_srv(db: Session, name: str, data: dict) -> PaymentTypes:
    payment_type = get_payment_type_by_name_srv(db=db, name=name)
    try:
        for key, value in data.items():
            if hasattr(payment_type, key):
                setattr(payment_type, key, value)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PaymentTypeAlreadyExists

    return payment_type


def create_payment_type_srv(db: Session, name: str, data: dict) -> PaymentTypes:
    payment_type = PaymentTypes(**data)
    try:
        db.add(payment_type)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PaymentTypeAlreadyExists
    return payment_type
