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

    # `dump_only=True`: ID knihy je generováno databází, takže ho pouze vracíme (serializujeme).
    book_id = fields.Int(dump_only=True)
    # `required=True`: Název knihy je povinný atribut při serializaci.
    title = fields.Str(required=True)
    # `allow_none=True`: Rok vydání může být `None` (pokud není znám).
    publication_year = fields.Int(allow_none=True)
    # `allow_none=True`: ISBN může být `None`.
    isbn = fields.Str(allow_none=True)
    # `allow_none=True`: Počet stran může být `None`.
    page_count = fields.Int(allow_none=True)
    # `fields.Decimal`: Pro práci s finančními hodnotami, aby se předešlo chybám zaokrouhlení s float.
    # `as_string=True`: Serializuje desetinné číslo jako řetězec (např. "123.45").
    # `allow_none=True`: Cena může být `None`.
    # `places=2`: Určuje počet desetinných míst.
    price = fields.Decimal(as_string=True, allow_none=True, places=2)

    # `fields.Nested`: Vnořené schéma pro zobrazení informací o vydavateli.
    # `"PublisherSchema"`: Název schématu, které se má vnořit (může být string, pokud je definováno později nebo v jiném modulu, aby se předešlo cyklickým importům).
    # `only=("publisher_id", "name")`: Z vnořeného PublisherSchema se vyberou pouze uvedené atributy.
    # `allow_none=True`: Kniha nemusí mít přiřazeného vydavatele.
    publisher = fields.Nested(
        "PublisherSchema", only=("publisher_id", "name"), allow_none=True
    )

    # `fields.List`: Definuje seznam.
    # `fields.Nested("AuthorSchema", ...)`: Seznam bude obsahovat objekty serializované pomocí AuthorSchema.
    # `only=(...)`: Z každého autora v seznamu se vyberou pouze specifikované atributy.
    # Toto pole bude obsahovat seznam autorů knihy.
    authors = fields.List(
        fields.Nested("AuthorSchema", only=(
            # Zobrazí ID, křestní jméno a příjmení autora.
            "author_id", "first_name", "last_name"))
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
            min=1, max=255, error="Název knihy musí mít 1 až 255 znaků."
        ),
    )
    # `allow_none=True`: Rok vydání může být `None`.
    # `required=False`: Rok vydání není povinný při vytváření knihy.
    # `validate=validate.Range(...)`: Validace číselného rozsahu.
    publication_year = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(min=0, error="Rok vydání nesmí být záporný."),
    )
    # `allow_none=True`: ISBN může být `None`.
    # `required=False`: ISBN není povinné.
    # `validate=validate.Length(equal=13)`: ISBN musí mít přesně 13 znaků.
    isbn = fields.Str(
        allow_none=True,
        required=False,
        validate=validate.Length(
            equal=13, error="ISBN musí mít přesně 13 znaků."  # Např. pro ISBN-13
        ),
    )
    # `allow_none=True`: Počet stran může být `None`.
    # `required=False`: Počet stran není povinný.
    # `validate=validate.Range(min=1)`: Počet stran musí být alespoň 1.
    page_count = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(
            min=1, error="Počet stran musí být alespoň 1."),
    )
    # `as_string=True`: Očekává a zpracovává cenu jako řetězec, ale interně ji převede na Decimal.
    # `allow_none=True`, `required=False`: Cena není povinná a může být `None`.
    # `places=2`: Počet desetinných míst pro validaci a zpracování.
    # `validate=validate.Range(min=0)`: Cena nesmí být záporná.
    price = fields.Decimal(
        as_string=True,
        allow_none=True,
        required=False,
        places=2,
        validate=validate.Range(min=0, error="Cena nesmí být záporná."),
    )
    # `publisher_id`: ID existujícího vydavatele, ke kterému bude kniha přiřazena.
    # `required=False`, `allow_none=True`: Není povinné a může být `None`.
    # `error_messages={"invalid": ...}`: Vlastní chybová hláška, pokud hodnota není platné celé číslo.
    publisher_id = fields.Int(
        required=False, allow_none=True,
        error_messages={"invalid": "ID vydavatele musí být celé číslo."}
    )
    # `author_ids`: Seznam ID existujících autorů, kteří napsali knihu.
    # `fields.List(fields.Int())`: Očekává seznam celých čísel.
    # `required=False`: Seznam autorů není povinný.
    author_ids = fields.List(
        fields.Int(), required=False
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
            min=1, max=255, error="Název knihy musí mít 1 až 255 znaků."
        ),
    )
    # `required=False`, `allow_none=True`: Rok vydání není povinný a může být `None`.
    publication_year = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(min=0, error="Rok vydání nesmí být záporný."),
    )
    # `required=False`, `allow_none=True`: ISBN není povinné a může být `None`.
    isbn = fields.Str(
        allow_none=True,
        required=False,
        validate=validate.Length(
            equal=13, error="ISBN musí mít přesně 13 znaků."  # Např. pro ISBN-13
        ),
    )
    # `required=False`, `allow_none=True`: Počet stran není povinný a může být `None`.
    page_count = fields.Int(
        allow_none=True,
        required=False,
        validate=validate.Range(
            min=1, error="Počet stran musí být alespoň 1."),
    )
    # `required=False`, `allow_none=True`: Cena není povinná a může být `None`.
    price = fields.Decimal(
        as_string=True,
        allow_none=True,
        required=False,
        places=2,
        validate=validate.Range(min=0, error="Cena nesmí být záporná."),
    )
    # `required=False`, `allow_none=True`: ID vydavatele není povinné a může být `None`.
    publisher_id = fields.Int(
        required=False, allow_none=True,
        error_messages={"invalid": "ID vydavatele musí být celé číslo."}
    )
    # `required=False`: Seznam ID autorů není povinný.
    author_ids = fields.List(
        fields.Int(), required=False
    )
