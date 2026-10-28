from datetime import date
from typing import Annotated, List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UsersBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None
    email: EmailStr
    created_at: date
    status: bool


class UsersRegister(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]


class UsersOut(UsersBase):
    uuid: UUID
    roles: List["RolesOut"] = []


class UsersInstructorOut(UsersBase):
    pass


class UsersAdminOut(UsersBase):
    roles: List["RolesOut"] = []


class UsersUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    password: Optional[str] = None


class UsersAdminUpdate(BaseModel):
    uuid: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    status: Optional[bool] = None
    roles: Optional[List["RolesOut"]] = None


class UsersLogin(BaseModel):
    email: EmailStr
    password: str
