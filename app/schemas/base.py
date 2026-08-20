from marshmallow import Schema


class BaseSchema(Schema):
    def __init__(self, *args, **kwargs):
        kwargs.pop("session", None)
        super().__init__(*args, **kwargs)
