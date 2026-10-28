<!-- Load when: Improving OpenAPI/docs -->

# OpenAPI — FastAPI Automatic Docs

FastAPI generates OpenAPI schema automatically at `/openapi.json` and interactive docs at `/docs`. Add metadata to improve generated docs.

## Pattern

### Router descriptions

```python
@router.get("/", response_model=List[RolesOut], summary="List all roles")
def list_roles(...):
```

```python
@router.post("/", response_model=RolesOut, status_code=status.HTTP_201_CREATED, summary="Create a role")
def create_role(...):
```

### Schema examples

```python
class UsersRegister(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: Optional[str] = None
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "first_name": "Jane",
            "last_name": "Doe",
            "phone_number": "+1234567890",
            "email": "jane@example.com",
            "password": "password123",
        }
    })
```

Key rules:
- Add `description` and `summary` to route decorators for non-trivial endpoints
- Add `json_schema_extra` examples to input schemas for `/docs` try-it-out
- Tags are set per router (`tags=["users"]`, `tags=["roles"]`, etc.)
- Operation IDs auto-generated from function names
- `response_model` drives response schema in OpenAPI

## Example — Users router with descriptions

See `app/routers/users.py`:
- Routes have `response_model` and status codes
- Login route returns `{"msg", "access_token", "user": {...}}`
