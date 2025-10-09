from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt

from app.errors import PermissionDeniedDisabledUser, PermissionDenied
from app.schemas import RolesSchema
from app.services.roles import get_roles_srv, get_user_roles_srv, add_user_role_srv, del_user_role_srv
from ..extensions import db

roles_bp = Blueprint("roles", __name__, url_prefix='/v1/roles')


@roles_bp.get("/")
@jwt_required()
def get_roles_endp():
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    roles = get_roles_srv()

    schema = RolesSchema(many=True)
    return {"data": schema.dump(roles)}, 200


@roles_bp.get("/me")
@jwt_required()
def get_my_roles_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    user_email = jwt_data["sub"]
    roles = get_user_roles_srv(email=user_email)

    schema = RolesSchema(many=True)
    return {"data": schema.dump(roles)}, 200


@roles_bp.get("/<string:email>")
@jwt_required()
def get_user_roles_endp(email: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    roles = get_user_roles_srv(email=email)

    schema = RolesSchema(many=True)
    return {"data": schema.dump(roles)}, 200


@roles_bp.post("/<string:email>/<string:role>")
@jwt_required()
def add_user_role_endp(email: str, role: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    schema = RolesSchema(session=db.session, many=True)
    roles = add_user_role_srv(email=email, role_name=role)
    return {"data": schema.dump(roles)}, 201


@roles_bp.delete("/<string:email>/<string:role>")
@jwt_required()
def delete_user_role_endp(email: str, role: str):
    """
    By business logic, the User role cannot be revoked
    """
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    schema = RolesSchema(session=db.session, many=True)
    roles = del_user_role_srv(email=email, role_name=role)
    return {"data": schema.dump(roles)}, 200
