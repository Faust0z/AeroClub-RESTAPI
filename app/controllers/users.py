from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import get_jwt, create_access_token, jwt_required
from marshmallow import ValidationError

from ..errors import PermissionDenied, BadAuthRequest, PermissionDeniedDisabledUser
from ..extensions import db
from ..schemas import UsersRegisterSchema, UsersSchema, UsersAdminSchema, UsersInstructorSchema, UsersUpdateSchema, \
    UsersAdminUpdateSchema
from ..services.users import get_users_srv, register_user_srv, update_user_srv, disable_user_srv, authenticate_user_srv, \
    get_user_by_email_srv

users_bp = Blueprint("users", __name__, url_prefix='/v1/users')


@users_bp.get("/")
@jwt_required()
def get_users_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    caller_roles = jwt_data.get("roles", ["User"])
    if "Admin" in caller_roles:
        schema = UsersAdminSchema(many=True)
    elif "Instructor" in caller_roles:
        schema = UsersInstructorSchema(many=True)
    else:
        raise PermissionDenied

    # Filters
    email = request.args.get("email")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    role = request.args.get("role_name")
    users = get_users_srv(
        email=email,
        first_name=first_name,
        last_name=last_name,
        role_name=role
    )

    return {"data": schema.dump(users)}, 200


@users_bp.get("/me")
@jwt_required()
def get_my_info_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    user_email = jwt_data["sub"]

    user = get_user_by_email_srv(user_email)

    schema = UsersSchema()
    return {"data": schema.dump(user)}, 200


@users_bp.get("/<string:email>")
@jwt_required()
def get_user_by_email_endp(email: str):
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    caller_roles = jwt_data.get("roles", ["User"])
    if "Admin" in caller_roles:
        schema = UsersAdminSchema()
    elif "Instructor" in caller_roles:
        schema = UsersInstructorSchema()
    else:
        raise PermissionDenied

    user = get_user_by_email_srv(email=email)

    return {"data": schema.dump(user)}, 200


@users_bp.patch("/<string:email>")
@jwt_required()
def update_user_endp(email: str):
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    user_email = jwt_data["sub"]
    caller_roles = jwt_data.get("roles", ["User"])
    if "Admin" in caller_roles:
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
@jwt_required()
def delete_user_endp(email: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    user = disable_user_srv(email=email)

    schema = UsersAdminSchema()
    return {"data": schema.dump(user)}, 200


@users_bp.post("/register")
def register_user_endp():
    schema = UsersRegisterSchema(session=db.session)
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    user = register_user_srv(user=data)
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
