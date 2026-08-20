from flask import Blueprint, request
from flask_jwt_extended import get_jwt
from marshmallow import ValidationError

from ..decorators import active_account_required, admin_required
from ..schemas import TransactionsAdminSchema, TransactionsPublicSchema
from ..services.transactions import get_transactions_srv, get_user_trans_by_email_srv, sum_user_transaction_srv

transactions_bp = Blueprint("transactions", __name__, url_prefix="/v1/transactions")


@transactions_bp.get("/")
@admin_required
def get_transactions_endp():
    email = request.args.get("email")
    first_name = request.args.get("first_name")
    last_name = request.args.get("last_name")
    payment_type = request.args.get("payment_type")
    starting_date = request.args.get("starting_date")
    limit_date = request.args.get("limit_date")
    transactions = get_transactions_srv(
        email=email,
        first_name=first_name,
        last_name=last_name,
        payment_type=payment_type,
        starting_date=starting_date,
        limit_date=limit_date
    )

    schema = TransactionsAdminSchema(many=True)
    return {"data": schema.dump(transactions)}, 200


@transactions_bp.get("/me")
@active_account_required
def get_my_transactions_endp():
    transactions = get_user_trans_by_email_srv(email=get_jwt()["sub"])

    schema = TransactionsPublicSchema(many=True)
    return {"data": schema.dump(transactions)}, 200


@transactions_bp.get("/<string:email>")
@admin_required
def get_user_transactions_endp(email: str):
    transactions = get_user_trans_by_email_srv(email=email)

    schema = TransactionsAdminSchema(many=True)
    return {"data": schema.dump(transactions)}, 200


@transactions_bp.post("/<string:email>")
@admin_required
def create_user_transaction_endp(email: str):
    schema = TransactionsPublicSchema()
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    transaction = sum_user_transaction_srv(email=email, data=data)
    return {"data": schema.dump(transaction)}, 201