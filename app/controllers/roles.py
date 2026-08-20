from flask import Blueprint
from flask_jwt_extended import get_jwt

from ..decorators import active_account_required, admin_required
from ..schemas import RolesSchema
from ..services.roles import get_roles_srv, get_user_roles_srv, add_user_role_srv, del_user_role_srv

roles_bp = Blueprint("roles", __name__, url_prefix="/v1/roles")


@roles_bp.get("/")
@admin_required
def get_roles_endp():
    roles = get_roles_srv()

    schema = RolesSchema(many=True)
    return {"data": schema.dump(roles)}, 200


@roles_bp.get("/me")
@active_account_required
def get_my_roles_endp():
    roles = get_user_roles_srv(email=get_jwt()["sub"])

    schema = RolesSchema(many=True)
    return {"data": schema.dump(roles)}, 200


@roles_bp.get("/<string:email>")
@admin_required
def get_user_roles_endp(email: str):
    roles = get_user_roles_srv(email=email)

    schema = RolesSchema(many=True)
    return {"data": schema.dump(roles)}, 200


@roles_bp.post("/<string:email>/<string:role>")
@admin_required
def add_user_role_endp(email: str, role: str):
    schema = RolesSchema(many=True)
    roles = add_user_role_srv(email=email, role_name=role)
    return {"data": schema.dump(roles)}, 201


@roles_bp.delete("/<string:email>/<string:role>")
@admin_required
def delete_user_role_endp(email: str, role: str):
    """The User role cannot be revoked (business rule)."""
    schema = RolesSchema(many=True)
    roles = del_user_role_srv(email=email, role_name=role)
    return {"data": schema.dump(roles)}, 200