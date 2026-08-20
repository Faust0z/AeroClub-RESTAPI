from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, create_access_token
from marshmallow import ValidationError

from ..decorators import active_account_required, admin_required
from ..errors import PermissionDenied, BadAuthRequest, PermissionDeniedDisabledUser
from ..schemas import (
    UsersRegisterSchema, UsersSchema, UsersAdminSchema, UsersInstructorSchema,
    UsersUpdateSchema, UsersAdminUpdateSchema,
)
from ..services.users import (
    get_users_srv, register_user_srv, update_user_srv, disable_user_srv,
    authenticate_user_srv, get_user_by_email_srv,
)

users_bp = Blueprint("users", __name__, url_prefix="/v1/users")


@users_bp.get("/")
@active_account_required
@admin_or_instructor_required
def get_users_endp():
    caller_roles = get_jwt().get("roles", ["User"])
    if "Admin" in caller_roles:
        schema = UsersAdminSchema(many=True)
    else:
        schema = UsersInstructorSchema(many=True)

    email = request.args.get("email")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    role = request.args.get("role_name")
    users = get_users_srv(email=email, first_name=first_name, last_name=last_name, role_name=role)

    return {"data": schema.dump(users)}, 200


@users_bp.get("/me")
@active_account_required
def get_my_info_endp():
    user = get_user_by_email_srv(get_jwt()["sub"])
    schema = UsersSchema()
    return {"data": schema.dump(user)}, 200


@users_bp.get("/<string:email>")
@active_account_required
@admin_or_instructor_required
def get_user_by_email_endp(email: str):
    caller_roles = get_jwt().get("roles", ["User"])
    if "Admin" in caller_roles:
        schema = UsersAdminSchema()
    else:
        schema = UsersInstructorSchema()

    user = get_user_by_email_srv(email=email)

    return {"data": schema.dump(user)}, 200


@users_bp.patch("/<string:email>")
@active_account_required
def update_user_endp(email: str):
    user_email = get_jwt()["sub"]
    if "Admin" in get_jwt().get("roles", []):
        schema = UsersAdminUpdateSchema(partial=True)
    elif user_email == email:
        schema = UsersUpdateSchema(partial=True)
    else:
        raise PermissionDenied

    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400
    user = update_user_srv(email=email, data=data)

    return {"data": schema.dump(user)}, 200


@users_bp.delete("/<string:email>")
@admin_required
def delete_user_endp(email: str):
    user = disable_user_srv(email=email)

    schema = UsersAdminSchema()
    return {"data": schema.dump(user)}, 200


@users_bp.post("/register")
def register_user_endp():
    schema = UsersRegisterSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    user = register_user_srv(data=data)
    return {"data": schema.dump(user)}, 201


@users_bp.post("/login")
def login_endp():
    email = request.json.get("email")
    password = request.json.get("password")

    if not email and password:
        raise BadAuthRequest

    user = authenticate_user_srv(email, password)

    if not user.status:
        raise PermissionDeniedDisabledUser

    roles = [role.name for role in user.roles] if user.roles else ["User"]
    additional_claims = {
        "roles": roles,
        "status": user.status
    }

    access_token = create_access_token(
        identity=user.email,
        additional_claims=additional_claims,
        expires_delta=timedelta(hours=24)
    )

    return {
        "msg": "Login successful",
        "access_token": access_token,
        "user": {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "roles": roles
        }
    }, 200