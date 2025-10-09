from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt

from ..errors import PermissionDeniedDisabledUser, PermissionDenied
from ..schemas import BalancesSchema, BalancesUpdateSchema
from ..services.balances import get_user_balance_by_email_srv, get_balances_srv

balances_bp = Blueprint("balances", __name__, url_prefix='/v1/balances')


@balances_bp.get("/")
@jwt_required()
def get_balances_endp():
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    min_balance = request.args.get("min_balance", type=float)
    max_balance = request.args.get("max_balance", type=float)
    balances = get_balances_srv(min_balance=min_balance, max_balance=max_balance)

    schema = BalancesUpdateSchema(many=True)
    return {"data": schema.dump(balances)}, 200


@balances_bp.get("/<string:email>")
@jwt_required()
def get_user_balance_endp(email: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    balance = get_user_balance_by_email_srv(email=email)

    schema = BalancesUpdateSchema()
    return {"data": schema.dump(balance)}, 200


@balances_bp.get("/me")
@jwt_required()
def get_my_balance_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    user_email = jwt_data["sub"]
    balance = get_user_balance_by_email_srv(email=user_email)

    schema = BalancesSchema()
    return {"data": schema.dump(balance)}, 200
