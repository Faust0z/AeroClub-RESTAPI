from marshmallow import fields, validate
from .base import BaseSchema


class UsersRegisterSchema(BaseSchema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone_number = fields.Str(required=True)
    address = fields.Str(allow_none=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))


class UsersSchema(BaseSchema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    phone_number = fields.Str(required=True)
    address = fields.Str(allow_none=True)
    email = fields.Email(dump_only=True)
    created_at = fields.Date(dump_only=True)
    roles = fields.Nested("RolesSchema", many=True, dump_only=True)


class UsersUpdateSchema(BaseSchema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    phone_number = fields.Str(required=False)
    address = fields.Str(allow_none=True)
    password = fields.Str(required=False, load_only=True)
    roles = fields.Nested("RolesUserUpdateSchema", many=True, dump_only=True)


class UsersAdminUpdateSchema(BaseSchema):
    id = fields.Int(dump_only=True)
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    phone_number = fields.Str(required=False)
    address = fields.Str(allow_none=True)
    email = fields.Email(required=False)
    password = fields.Str(required=False, load_only=True)
    roles = fields.List(fields.Nested("RolesUpdateSchema"), required=False)


class UsersInstructorSchema(BaseSchema):
    first_name = fields.Str(required=True, dump_only=True)
    last_name = fields.Str(required=True, dump_only=True)
    phone_number = fields.Str(required=True, dump_only=True)
    email = fields.Email(dump_only=True)
    status = fields.Bool(dump_only=True)


class UsersAdminSchema(BaseSchema):
    first_name = fields.Str(required=False)
    last_name = fields.Str(required=False)
    phone_number = fields.Str(required=False)
    address = fields.Str(allow_none=True)
    email = fields.Email(required=False)
    status = fields.Bool(required=False)
    roles = fields.Nested("RolesSchema", many=True, required=False)