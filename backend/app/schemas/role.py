from marshmallow import Schema, fields
# from marshmallow_sqlalchemy import SQLAlchemyAutoSchema # Již není potřeba
# from app.models import Role # Již není potřeba pro explicitní definici schématu


class RoleSchema(Schema):
    """
    Schéma pro serializaci dat o roli.
    """
    class Meta:
        title = "RoleSchema"  # Název schématu pro OpenAPI dokumentaci
    id = fields.Integer(dump_only=True, description="Unikátní ID role.")
    name = fields.String(
        required=True, description="Název role (např. admin, editor).")
    description = fields.String(
        allow_none=True, description="Volitelný popis role.")


class UserRoleAssignSchema(Schema):
    class Meta:
        title = "UserRoleAssignSchema"  # Název schématu pro OpenAPI dokumentaci
    role_id = fields.Integer(
        required=True, description="ID role, která má být přiřazena.")
