from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

from app.errors import PermissionDenied, PermissionDeniedDisabledUser
from app.schemas import FlightSessionsSchema, FlightSessionsCreateSchema
from app.services.flight_sessions import get_flight_sessions_srv, get_user_flight_sessions_srv, \
    create_flight_session_srv, get_flight_session_by_identifier_srv

flight_sessions_bp = Blueprint("flight_sessions", __name__, url_prefix='/v1/flight_sessions')


@flight_sessions_bp.get("/")
@jwt_required()
def get_flight_sessions_endp():
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    flight_session_identifier = request.args.get("flight_session_identifier")
    plane_registration = request.args.get("plane_registration")
    admin_email = request.args.get("admin_email")
    user_first_name = request.args.get("user_first_name")
    user_last_name = request.args.get("user_last_name")
    observations = request.args.get("observations")
    starting_date = request.args.get("starting_date")
    limit_date = request.args.get("limit_date")
    flight_sessions = get_flight_sessions_srv(
        flight_session_identifier=flight_session_identifier,
        plane_registration=plane_registration,
        admin_email=admin_email,
        user_first_name=user_first_name,
        user_last_name=user_last_name,
        observations=observations,
        starting_date=starting_date,
        limit_date=limit_date
    )

    schema = FlightSessionsSchema(many=True)
    return {"data": schema.dump(flight_sessions)}, 200


@flight_sessions_bp.get("/me")
@jwt_required()
def get_my_flight_sessions_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    user_email = jwt_data["sub"]
    flight_sessions = get_user_flight_sessions_srv(user_email)

    schema = FlightSessionsSchema(many=True)
    return {"data": schema.dump(flight_sessions)}, 200


@flight_sessions_bp.get("/by-email/<string:email>")
@jwt_required()
def get_user_flight_sessions_endp(email: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    flight_sessions = get_user_flight_sessions_srv(email=email)

    schema = FlightSessionsSchema(many=True)
    return {"data": schema.dump(flight_sessions)}, 200


@flight_sessions_bp.get("/<int:flight_session_identifier>")
@jwt_required()
def get_flight_sessions_by_identifier_endp(flight_session_identifier: int):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    flight_sessions = get_flight_session_by_identifier_srv(flight_session_identifier=flight_session_identifier)

    schema = FlightSessionsSchema()
    return {"data": schema.dump(flight_sessions)}, 200


@flight_sessions_bp.post("/")
@jwt_required()
def create_flight_sessions_endp():
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    try:
        data = FlightSessionsCreateSchema().load(request.get_json())
        print(data)
    except ValidationError as err:
        return {"errors": err.messages}, 400
    admin_email = jwt_data["sub"]
    flight_session = create_flight_session_srv(
        flight_session_data=data,
        admin_email=admin_email
    )
    return {"data": FlightSessionsSchema().dump(flight_session)}, 201
