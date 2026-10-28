<!-- Load when: Adding or editing error handling -->

# Errors — AppError Hierarchy

All domain exceptions live under `app/errors.py`. They subclass `AppError` with `status_code` and `detail` class attributes.

## Pattern

```python
class AppError(Exception):
    status_code: int = 500
    detail: str = "An unexpected error occurred"


class UserNotFound(AppError):
    status_code = 404
    detail = "No user found with the given email"


class EmailAlreadyExists(AppError):
    status_code = 409
    detail = "The email given is already registered"
```

Key rules:
- All domain exceptions inherit from `AppError`
- `status_code` and `detail` are class attributes
- Raised from services, caught in routers, converted to `HTTPException`
- Global handler in `app/main.py` maps `AppError` → `JSONResponse(status_code, {"detail": ...})`
- No Flask/Werkzeug imports — all framework-agnostic

## Example — Error classes

See `app/errors.py`:
- `UserNotFound` (404), `EmailAlreadyExists` (409), `AuthError` (401), `PermissionDenied` (403), `PermissionDeniedDisabledUser` (403), `BadTimeInput` (400), `FlightSessionNotFound` (404), etc.

## Example — Router error handling

```python
try:
    user = get_user_by_id_srv(db=db, user_id=user_id)
except UserNotFound:
    raise HTTPException(status_code=404, detail="User not found")
```

## Exception handler

See `app/main.py`:
```python
@app.exception_handler(AppError)
async def app_error_handler(request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
```
