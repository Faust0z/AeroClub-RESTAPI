from flask import Blueprint, request
from flask_jwt_extended import get_jwt

from ..decorators import active_account_required, admin_required
from ..schemas import BalancesSchema, BalancesUpdateSchema
from ..services.balances import get_user_balance_by_email_srv, get_balances_srv

balances_bp = Blueprint("balances", __name__, url_prefix="/v1/balances")


@balances_bp.get("/")
@admin_required
def get_balances_endp():
    min_balance = request.args.get("min_balance", type=float)
    max_balance = request.args.get("max_balance", type=float)
    balances = get_balances_srv(min_balance=min_balance, max_balance=max_balance)

    schema = BalancesUpdateSchema(many=True)
    return {"data": schema.dump(balances)}, 200


@balances_bp.get("/<string:email>")
@admin_required
def get_user_balance_endp(email: str):
    balance = get_user_balance_by_email_srv(email=email)

    schema = BalancesUpdateSchema()
    return {"data": schema.dump(balance)}, 200


@balances_bp.get("/me")
@active_account_required
def get_my_balance_endp():
    balance = get_user_balance_by_email_srv(email=get_jwt()["sub"])

    schema = BalancesSchema()
    return {"data": schema.dump(balance)}, 200