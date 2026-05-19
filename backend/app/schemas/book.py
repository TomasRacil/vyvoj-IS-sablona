from marshmallow import Schema, fields, validate

# --- Schémata pro model Book ---


class BookSchema(Schema):
    """
    Základní schéma pro serializaci objektu Book.
    Používá se typicky pro odpovědi API (GET požadavky).
    Zobrazuje informace o knize včetně zjednodušených informací o autorech a vydavateli.
    Serializace: Objekt Pythonu -> JSON
    """

    class Meta:
        # Název schématu pro OpenAPI/Swagger dokumentaci.
        title = "BookSchema"

    # `dump_only=True`: ID knihy je generováno databází
    id = fields.UUID(dump_only=True)
    # `required=True`: Název knihy je povinný atribut při serializaci.
    title = fields.Str(required=True)
    # `allow_none=True`: Rok vydání může být `None`
    published_year = fields.Int(allow_none=True)
    # `allow_none=True`: ISBN může být `None`.
    isbn = fields.Str(allow_none=True)

    # `fields.Nested`: Vnořené schéma pro zobrazení informací o vydavateli.
    publisher = fields.Nested(
        "PublisherSchema", only=("id", "name"), allow_none=True
    )

    # `fields.List`: Definuje seznam.
    authors = fields.List(
        fields.Nested("AuthorSchema", only=(
            "id", "first_name", "last_name"))
    )


class BookCreateSchema(Schema):
    """
    Schéma specificky navržené pro deserializaci a validaci dat
    při vytváření nové knihy (POST požadavek).
    Používá se hlavně pro validaci vstupních dat.
    """

    class Meta:
        title = "BookCreateSchema"  # Název schématu pro OpenAPI dokumentaci

    # `required=True`: Název knihy je povinný při vytváření.
    # `validate=validate.Length(...)`: Validace délky názvu.
    # `error`: Vlastní chybová hláška pro případ neúspěšné validace.
    title = fields.Str(
        required=True,
        validate=validate.Length(
            min=1, max=200, error="Název knihy musí mít 1 až 200 znaků."
        ),
    )
    published_year = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(min=0, error="Rok vydání nesmí být záporný."),
    )
    isbn = fields.Str(
        allow_none=True,
        required=False,
        validate=validate.Length(
            max=20, error="ISBN může mít maximálně 20 znaků."
        ),
    )
    publisher_id = fields.UUID(
        required=False, allow_none=True
    )
    author_ids = fields.List(
        fields.UUID(), required=False
    )


class BookUpdateSchema(Schema):
    """
    Schéma pro aktualizaci existující knihy (PUT/PATCH požadavek).
    Všechna pole jsou zde typicky `required=False`, aby bylo možné aktualizovat
    pouze některé atributy knihy (částečná aktualizace, PATCH).
    Pro PUT by se mohlo zvážit `required=True` pro některá pole, pokud by se vyžadovala kompletní náhrada.
    """

    class Meta:
        title = "BookUpdateSchema"  # Název schématu pro OpenAPI dokumentaci

    # `required=False`: Název není povinný při aktualizaci.
    title = fields.Str(
        required=False,
        validate=validate.Length(
            min=1, max=200, error="Název knihy musí mít 1 až 200 znaků."
        ),
    )
    published_year = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(min=0, error="Rok vydání nesmí být záporný."),
    )
    isbn = fields.Str(
        allow_none=True,
        required=False,
        validate=validate.Length(
            max=20, error="ISBN může mít maximálně 20 znaků."
        ),
    )
    publisher_id = fields.UUID(
        required=False, allow_none=True
    )
    author_ids = fields.List(
        fields.UUID(), required=False
    )
