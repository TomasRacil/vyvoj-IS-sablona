from marshmallow import Schema, fields, validate


# --- Schémata pro model Author ---


class AuthorSchema(Schema):
    """
    Základní schéma pro serializaci objektu Author.
    Používá se typicky pro odpovědi API (GET požadavky).
    Serializace: Objekt Pythonu -> JSON
    """
    class Meta:
        # Název schématu pro OpenAPI/Swagger dokumentaci.
        title = "AuthorSchema"

    # `dump_only=True`: ID autora je generováno databází
    id = fields.UUID(dump_only=True)
    # `required=True`: Křestní jméno je povinný atribut při serializaci.
    first_name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Křestní jméno musí mít 1 až 50 znaků."
        ),
    )
    # `required=True`: Příjmení je povinný atribut při serializaci.
    last_name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Příjmení musí mít 1 až 50 znaků."
        ),
    )
    # `allow_none=True`: Datum narození může být `None`
    birth_date = fields.Date(allow_none=True)
    # `fields.List(fields.Nested(...))`: Seznam knih napsaných tímto autorem.
    books = fields.List(fields.Nested(
        "BookSchema", only=("id", "title")))


class AuthorCreateSchema(Schema):
    """
    Schéma specificky navržené pro deserializaci a validaci dat
    při vytváření nového autora (POST požadavek).
    Používá se hlavně pro validaci vstupních dat.
    """
    class Meta:
        title = "AuthorCreateSchema"  # Název schématu pro OpenAPI dokumentaci

    # `required=True`: Křestní jméno je povinné při vytváření autora.
    first_name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Křestní jméno musí mít 1 až 50 znaků."
        ),
    )
    # `required=True`: Příjmení je povinné při vytváření autora.
    last_name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Příjmení musí mít 1 až 50 znaků."
        ),
    )
    # `allow_none=True`: Datum narození může být `None`.
    birth_date = fields.Date(allow_none=True, required=False)
