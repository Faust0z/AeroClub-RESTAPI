from functools import wraps

from flask_jwt_extended import get_jwt, jwt_required

from .errors import PermissionDenied, PermissionDeniedDisabledUser


def active_account_required(fn):
    """Require a valid JWT issued to an active (non-disabled) account."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if not get_jwt().get("status", True):
            raise PermissionDeniedDisabledUser
        return fn(*args, **kwargs)
    return wrapper


def admin_or_instructor_required(fn):
    """Require a valid JWT and the Admin or Instructor role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        caller_roles = get_jwt().get("roles", ["User"])
        if not ({"Admin", "Instructor"} & set(caller_roles)):
            raise PermissionDenied
        return fn(*args, **kwargs)
    return wrapper


def instructor_required(fn):
    """Require a valid JWT and the Instructor role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        caller_roles = get_jwt().get("roles", ["User"])
        if "Instructor" not in caller_roles:
            raise PermissionDenied
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    """Require a valid JWT and the Admin role."""
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        caller_roles = get_jwt().get("roles", ["User"])
        if "Admin" not in caller_roles:
            raise PermissionDenied
        return fn(*args, **kwargs)
    return wrapper