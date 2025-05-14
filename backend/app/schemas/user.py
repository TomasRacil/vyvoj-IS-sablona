from marshmallow import Schema, fields, validate

# --- Schémata pro model User ---


class UserSchema(Schema):
    """
    Základní schéma pro serializaci objektu User.
    Používá se typicky pro odpovědi API (GET požadavky).
    Nezahrnuje citlivá data jako heslo.
    Serializace: Objekt Pythonu -> JSON (pro odpověď API)
    Deserializace: JSON (z požadavku API) -> Objekt Pythonu (pro zpracování)
    """
    class Meta:
        # 'title' se používá pro generování dokumentace API (např. Swagger/OpenAPI).
        # Pomáhá identifikovat schéma v dokumentaci.
        title = "UserSchema"  # Název schématu pro OpenAPI dokumentaci

    # `dump_only=True`: Atribut bude zahrnut POUZE při serializaci (objekt -> JSON).
    # Při deserializaci (JSON -> objekt) bude ignorován.
    # Ideální pro ID generovaná databází nebo časová razítka vytvoření.
    id = fields.Int(dump_only=True)

    # `required=True`: Atribut je povinný při deserializaci (pokud by schéma bylo použito pro vstup).
    # Při serializaci musí mít objekt tento atribut (jinak chyba).
    # `validate=validate.Length(min=3)`: Validace zajišťuje, že řetězec má minimálně 3 znaky.
    username = fields.Str(required=True, validate=validate.Length(min=3))

    # `fields.Email`: Speciální typ pole, který automaticky validuje, zda je řetězec platnou emailovou adresou.
    # `required=True`: Email je povinný.
    email = fields.Email(required=True)

    # `dump_only=True`: Datum vytvoření je typicky generováno serverem/databází,
    # takže ho chceme pouze zahrnout v odpovědi (serializace), ne očekávat na vstupu.
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """
    Schéma specificky navržené pro deserializaci a validaci dat
    při vytváření nového uživatele (POST požadavek).
    Může se lišit od UserSchema (např. může obsahovat pole pro heslo).
    Používá se hlavně pro validaci vstupních dat.
    """
    class Meta:
        title = "UserCreateSchema"  # Název schématu pro OpenAPI dokumentaci

    # Pro vytvoření uživatele požadujeme 'username' a 'email'.
    # Validace jsou stejné jako v UserSchema.
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)

    # `load_only=True`: Atribut bude zpracován POUZE při deserializaci (JSON -> objekt).
    # Nebude nikdy zahrnut při serializaci (objekt -> JSON).
    # Ideální pro citlivá data jako hesla, která přijímáme, ale nikdy neposíláme zpět v odpovědi.
    # `validate=validate.Length(min=8)`: Heslo musí mít minimálně 8 znaků.
    # password = fields.Str(
    #     required=True,
    #     load_only=True,
    #     validate=validate.Length(min=8, error="Heslo musí mít alespoň 8 znaků.")
    # )
