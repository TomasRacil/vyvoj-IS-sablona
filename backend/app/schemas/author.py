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

    # `dump_only=True`: ID autora je generováno databází, takže ho pouze vracíme (serializujeme).
    author_id = fields.Int(dump_only=True)
    # `required=True`: Křestní jméno je povinný atribut při serializaci.
    # `validate=validate.Length(...)`: Validace délky jména.
    # `error`: Vlastní chybová hláška pro případ neúspěšné validace.
    first_name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Křestní jméno musí mít 1 až 50 znaků."
        ),
    )
    # `required=True`: Příjmení je povinný atribut při serializaci.
    # `validate=validate.Length(...)`: Validace délky příjmení.
    last_name = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=50, error="Příjmení musí mít 1 až 50 znaků."
        ),
    )
    # `allow_none=True`: Rok narození může být `None` (pokud není znám).
    # `validate=validate.Range(min=0)`: Validace zajišťuje, že rok narození není záporné číslo.
    # `error_messages={"validator_failed": ...}`: Vlastní chybová hláška pro neúspěšnou validaci `Range`.
    birth_year = fields.Int(
        allow_none=True,
        validate=validate.Range(
            min=0
        ),
        error_messages={
            "validator_failed": "Rok narození musí být kladné celé číslo."},
    )
    # `fields.List(fields.Nested(...))`: Seznam knih napsaných tímto autorem.
    # `only=("book_id", "title")`: Z každé knihy se zobrazí pouze ID a název.
    books = fields.List(fields.Nested(
        "BookSchema", only=("book_id", "title")))


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
    # `allow_none=True`: Rok narození může být `None`.
    # `required=False`: Rok narození není povinný při vytváření autora.
    # `validate=validate.Range(min=0)`: Validace číselného rozsahu.
    birth_year = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(min=0),
        error_messages={
            "validator_failed": "Rok narození musí být kladné celé číslo."},
    )
