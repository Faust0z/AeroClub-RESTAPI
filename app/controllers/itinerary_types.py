from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

from ..errors import PermissionDeniedDisabledUser, PermissionDenied
from ..schemas import ItineraryTypesSchema, ItineraryTypesUpdateSchema
from ..services.itinerary_types import update_itinerary_type_srv, get_itinerary_types_srv

itinerary_types_bp = Blueprint("itinerary_types", __name__, url_prefix="/v1/itinerary_types")


@itinerary_types_bp.get("/")
@jwt_required()
def get_itinerary_types_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    itinerary_types = get_itinerary_types_srv()

    schema = ItineraryTypesSchema(many=True)
    return {"data": schema.dump(itinerary_types)}, 200


@itinerary_types_bp.patch("/<string:type>")
@jwt_required()
def update_itinerary_type_endp(type: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    schema = ItineraryTypesUpdateSchema(partial=True)
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400
    Itinerary_type = update_itinerary_type_srv(type=type, data=data)
    return {"data": schema.dump(Itinerary_type)}, 200
