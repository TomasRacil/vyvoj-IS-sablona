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

    # `dump_only=True`: ID vydavatele je generováno databází, takže ho pouze vracíme (serializujeme).
    publisher_id = fields.Int(dump_only=True)
    # `required=True`: Název vydavatele je povinný atribut při serializaci.
    # `validate=validate.Length(...)`: Validace délky názvu.
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # `allow_none=True`: Sídlo může být `None` (pokud není známo nebo relevantní).
    headquarters = fields.Str(allow_none=True)
    # `fields.List`: Definuje seznam.
    # `fields.Nested("BookSchema", ...)`: Seznam bude obsahovat objekty serializované pomocí BookSchema.
    # `only=("book_id", "title")`: Z každé knihy v seznamu se vybere pouze ID a název.
    # Toto pole bude obsahovat seznam knih vydaných tímto vydavatelem.
    books = fields.List(fields.Nested("BookSchema", only=("book_id", "title")))


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
    # `allow_none=True`: Sídlo může být `None`. Při vytváření není povinné (protože `required` není `True`).
    headquarters = fields.Str(allow_none=True)


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
    headquarters = fields.Str(allow_none=True)
