from marshmallow import Schema, fields, validate

# --- Schémata pro model Publisher ---


class PublisherSchema(Schema):
    """
    Základní schéma pro serializaci objektu Publisher.
    Používá se typicky pro odpovědi API (GET požadavky).
    Serializace: Objekt Pythonu -> JSON
    """
    class Meta:
        # Název schématu pro OpenAPI/Swagger dokumentaci.
        title = "PublisherSchema"

    # `dump_only=True`: ID vydavatele je generováno databází
    id = fields.UUID(dump_only=True)
    # `required=True`: Název vydavatele je povinný atribut při serializaci.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # `allow_none=True`: Sídlo může být `None`
    address = fields.Str(allow_none=True)
    # `fields.List`: Definuje seznam.
    books = fields.List(fields.Nested("BookSchema", only=("id", "title")))


class PublisherCreateSchema(Schema):
    """
    Schéma pro vytváření nového vydavatele.
    Používá se pro deserializaci a validaci dat z POST požadavku.
    """
    class Meta:
        title = "PublisherCreateSchema"  # Název schématu pro OpenAPI dokumentaci

    # `required=True`: Název vydavatele je povinný při vytváření.
    # `validate=validate.Length(...)`: Validace délky názvu.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # `allow_none=True`: Sídlo může být `None`.
    address = fields.Str(allow_none=True)


class PublisherUpdateSchema(Schema):
    """
    Schéma pro aktualizaci vydavatele.
    Používá se pro deserializaci a validaci dat z PUT/PATCH požadavku.
    Všechna pole jsou `required=False` pro umožnění částečných aktualizací (PATCH).
    """
    class Meta:
        title = "PublisherUpdateSchema"  # Název schématu pro OpenAPI dokumentaci
    # `required=False`: Název není povinný při aktualizaci.
    name = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    # `allow_none=True`, `required=False`: Sídlo není povinné a může být `None`.
    address = fields.Str(allow_none=True)
