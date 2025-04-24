from marshmallow import Schema, fields, validate


# Základní schéma pro uživatele (bez citlivých dat jako heslo)
class UserSchema(Schema):
    id = fields.Int(dump_only=True)  # Jen pro čtení (výstup z API)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)


# Schéma pro vytváření uživatele (může se lišit)
class UserCreateSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    # password = fields.Str(required=True, load_only=True)


# Přidejte schémata pro další modely
# class EventSchema(Schema):
#     id = fields.Int(dump_only=True)
#     name = fields.Str(required=True)
#     date = fields.Date(required=True)
