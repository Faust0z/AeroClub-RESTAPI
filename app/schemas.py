from marshmallow import fields, validate, post_load, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field

from .models import Users, Roles, Transactions, Planes, PlaneStatus, PaymentTypes, ItineraryTypes, Itineraries, \
    FlightSessions, Balances, AirportCodes
from .services.payment_types import get_payment_type_by_name_srv


class AirportCodesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AirportCodes
        load_instance = True
        include_fk = False
        exclude = ("id", "itineraries",)

    code = auto_field(required=True)


class AirportCodesCreateSchema(Schema):
    code = fields.Str(required=True)


class ItineraryTypesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ItineraryTypes
        load_instance = True
        include_fk = False
        exclude = ("id",)

    type = auto_field(required=True)


class ItinerariesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Itineraries
        load_instance = False
        include_fk = False
        exclude = ("id",)

    departure_time = auto_field(required=True)
    arrival_time = auto_field(required=True)
    landings_amount = auto_field(required=True)
    observations = auto_field(required=False, allow_none=True)
    itinerary_type = fields.Nested(ItineraryTypesSchema)
    airport_codes = fields.Nested(AirportCodesSchema, many=True)


class ItinerariesCreateSchema(Schema):
    departure_time = fields.DateTime(required=True)
    arrival_time = fields.DateTime(required=True)
    landings_amount = fields.Integer(required=True)
    observations = fields.Str(allow_none=True)
    itinerary_type = fields.Str(required=True)
    plane_registration = fields.Str(required=True)
    airport_codes = fields.Nested(AirportCodesCreateSchema, many=True, required=True)


class AirportCodesUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AirportCodes
        load_instance = False
        include_fk = False
        exclude = ()

    id = auto_field(dump_only=True)
    code = auto_field(required=True)
    itineraries = fields.Nested(ItinerariesSchema, many=True, dump_only=True)


class FlightSessionsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = FlightSessions
        load_instance = True
        include_fk = False
        exclude = ("id",)

    issued_date = auto_field(dump_only=True)
    observations = auto_field(required=False, allow_none=True)
    flight_session_identifier = auto_field(dump_only=True)
    itineraries = fields.Nested(ItinerariesSchema, many=True)


class FlightSessionsCreateSchema(Schema):
    user_email = fields.Email(required=True)
    instructor_email = fields.Email(allow_none=True)
    issued_date = fields.Date(required=True)
    observations = fields.Str(allow_none=True)
    itineraries = fields.Nested(ItinerariesCreateSchema, many=True, required=True)


# Includes itineraries and excludes airport_codes to avoid circular nesting
class AirportCodesWithItinerariesSchema(AirportCodesSchema):
    itineraries = fields.Nested(ItinerariesSchema, many=True, exclude=("airport_codes",))


class ItineraryTypesUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = ItineraryTypes
        load_instance = False
        include_fk = False
        exclude = ()

    id = auto_field(dump_only=True)
    type = auto_field(required=True)


class PaymentTypesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentTypes
        load_instance = True
        include_fk = False
        exclude = ("id",)

    type = auto_field(required=True)
    details = auto_field(required=False, allow_none=True)


class PaymentTypesUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentTypes
        load_instance = False
        include_fk = False
        exclude = ("id",)

    id = auto_field(dump_only=True)
    type = auto_field(required=False)
    details = auto_field(required=False, allow_none=True)


class PlaneStatusSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PlaneStatus
        load_instance = True
        include_fk = False
        exclude = ("id",)

    state = auto_field(required=True)


class PlaneStatusUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PlaneStatus
        load_instance = False
        include_fk = False
        exclude = ()

    id = auto_field(dump_only=True)
    state = auto_field(required=True)


class PlanesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Planes
        load_instance = True
        include_fk = False
        exclude = ("id",)

    brand = auto_field(required=True)
    model = auto_field(required=True)
    registration = auto_field(required=True)
    category = auto_field(required=True)
    acquisition_date = auto_field(required=False, allow_none=True)
    fare = auto_field(required=True)
    consumption_per_hour = auto_field(required=True)
    description = auto_field(required=False, allow_none=True)
    plane_status = fields.Nested(PlaneStatusSchema)


class PlanesUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Planes
        load_instance = False
        include_fk = False
        exclude = ()

    id = auto_field(dump_only=True)
    brand = auto_field(required=False)
    model = auto_field(required=False)
    registration = auto_field(required=False)
    category = auto_field(required=False)
    acquisition_date = auto_field(required=False, allow_none=True)
    fare = auto_field(required=False)
    consumption_per_hour = auto_field(required=False)
    description = auto_field(required=False, allow_none=True)
    plane_status = fields.Nested(PlaneStatusSchema)


class RolesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Roles
        load_instance = True
        include_fk = False
        exclude = ("id", "users",)

    name = auto_field(required=True, dump_only=True)


class RolesUserUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Roles
        load_instance = False
        include_fk = False
        exclude = ("id", "users",)

    name = auto_field(required=False, dump_only=True)


class RolesUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Roles
        load_instance = False
        include_fk = False
        exclude = ()

    id = auto_field(dump_only=True)
    name = auto_field(required=False)


class TransactionsBaseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transactions
        load_instance = False
        include_fk = False
        exclude = ("id",)

    amount = auto_field(required=True)
    issued_date = auto_field(required=True)
    description = auto_field(required=False, allow_none=True)


class TransactionsAdminSchema(TransactionsBaseSchema):
    exclude = ()

    id = auto_field(dump_only=True)
    payment_type = fields.Nested("PaymentTypesSchema")


class TransactionsPublicSchema(TransactionsBaseSchema):
    payment_type = fields.Method(serialize="get_payment_type_name", deserialize="load_payment_type")

    def load_payment_type(self, value):
        return get_payment_type_by_name_srv(name=value)

    def get_payment_type_name(self, obj):
        return obj.payment_type.type if obj.payment_type else None

    @post_load
    def make_transaction(self, data, **kwargs):
        return Transactions(**data)


class UsersRegisterSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        include_fk = False
        exclude = ("id", "created_at", "disabled_at", "status", "roles", "flight_sessions",)

    first_name = auto_field(required=True)
    last_name = auto_field(required=True)
    phone_number = auto_field(required=True)
    address = auto_field(required=False, allow_none=True)
    email = auto_field(required=True)
    password = auto_field(required=True, load_only=True, validate=validate.Length(min=8))


class UsersSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        include_fk = False
        exclude = ("id", "flight_sessions", "disabled_at", "status", "password",)

    first_name = auto_field(required=True)
    last_name = auto_field(required=True)
    phone_number = auto_field(required=True)
    address = auto_field(required=False, allow_none=True)
    email = auto_field(dump_only=True)
    created_at = auto_field(dump_only=True)
    roles = fields.Nested(RolesSchema, many=True, dump_only=True)


class UsersUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = False
        include_fk = False
        exclude = ("id", "flight_sessions", "disabled_at", "status",)

    first_name = auto_field(required=False)
    last_name = auto_field(required=False)
    phone_number = auto_field(required=False)
    address = auto_field(required=False, allow_none=True)
    password = auto_field(required=False, load_only=True)
    # plain dicts, not ORM
    roles = fields.Nested(RolesUserUpdateSchema, many=True, dump_only=True)


class UsersAdminUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = False
        include_fk = False
        exclude = ("flight_sessions", "status",)

    id = auto_field(dump_only=True)
    first_name = auto_field(required=False)
    last_name = auto_field(required=False)
    phone_number = auto_field(required=False)
    address = auto_field(required=False, allow_none=True)
    email = auto_field(required=False)
    password = auto_field(required=False, load_only=True)
    # plain dicts, not ORM
    roles = fields.List(fields.Nested(RolesUpdateSchema), required=False)


class UsersInstructorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        include_fk = False
        exclude = ("id", "flight_sessions", "address", "created_at", "disabled_at", "password", "roles")

    first_name = auto_field(required=True, dump_only=True)
    last_name = auto_field(required=True, dump_only=True)
    phone_number = auto_field(required=True, dump_only=True)
    email = auto_field(dump_only=True)
    status = auto_field(dump_only=True)


class BalancesSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Balances
        load_instance = True
        include_fk = False
        exclude = ("id",)

    balance = auto_field(required=True, dump_only=True)
    user = fields.Nested(UsersInstructorSchema)


class BalancesUpdateSchema(BalancesSchema):
    exclude = ()
    id = auto_field(dump_only=True)
    balance: auto_field(required=False)


class UsersAdminSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True
        include_fk = False
        exclude = ("flight_sessions", "password",)

    first_name = auto_field(required=False)
    last_name = auto_field(required=False)
    phone_number = auto_field(required=False)
    address = auto_field(required=False, allow_none=True)
    email = auto_field(required=False)
    status = auto_field(required=False)
    roles = fields.Nested(RolesSchema, many=True, required=False)
