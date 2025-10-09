from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt
from marshmallow import ValidationError

from app.errors import PermissionDeniedDisabledUser, PermissionDenied
from app.schemas import PlanesSchema, PlanesUpdateSchema
from app.services.planes import get_planes_srv, create_plane_srv, update_plane_srv, get_plane_by_registration_srv, \
    update_plane_status_srv
from ..extensions import db

planes_bp = Blueprint('planes', __name__, url_prefix='/v1/planes')


@planes_bp.get('/')
@jwt_required()
def get_planes_endp():
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    planes = get_planes_srv()

    schema = PlanesSchema(many=True)
    return {'data': schema.dump(planes)}, 200


@planes_bp.get('/<string:registration>')
@jwt_required()
def get_plane_by_registration_endp(registration: str):
    jwt_data = get_jwt()
    if not jwt_data.get("status", True):
        raise PermissionDeniedDisabledUser

    plane = get_plane_by_registration_srv(registration)

    schema = PlanesSchema()
    return {'data': schema.dump(plane)}, 200


@planes_bp.post('/')
@jwt_required()
def create_plane_endp():
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    schema = PlanesSchema(session=db.session)
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400

    plane = create_plane_srv(data)
    return {"data": schema.dump(plane)}, 201


@planes_bp.patch('/<string:registration>')
@jwt_required()
def update_plane_endp(registration: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    schema = PlanesUpdateSchema(partial=True)
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return {"errors": err.messages}, 400
    plane = update_plane_srv(registration=registration, data=data)

    return {"data": schema.dump(plane)}, 200


@planes_bp.patch('/<string:registration>/<string:plane_status>')
@jwt_required()
def update_plane_status_endp(registration: str, plane_status: str):
    jwt_data = get_jwt()
    caller_roles = jwt_data.get("roles", ["User"])
    if not "Admin" in caller_roles:
        raise PermissionDenied

    schema = PlanesUpdateSchema(partial=True)
    plane = update_plane_status_srv(registration=registration, plane_status=plane_status)

    return {"data": schema.dump(plane)}, 200
