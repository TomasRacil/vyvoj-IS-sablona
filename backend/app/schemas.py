# Tento soubor definuje schémata pomocí knihovny Marshmallow.
# Schémata slouží k:
# 1. Serializaci: Převod komplexních objektů (např. SQLAlchemy modely) na jednoduché Python datové typy (slovníky, seznamy),
#    které lze snadno převést na JSON pro API odpovědi.
# 2. Deserializaci: Převod jednoduchých datových typů (např. z JSON těla požadavku) na Python objekty.
# 3. Validaci: Kontrola, zda data (přijatá v požadavku nebo před serializací) splňují definovaná pravidla
#    (např. typ, povinnost, délka, formát).
# Flask-Smorest tato schémata využívá pro automatickou validaci požadavků (@arguments)
# a formátování odpovědí (@response).

from marshmallow import Schema, fields, validate

# --- Schémata pro model User ---


class UserSchema(Schema):
    """
    Základní schéma pro serializaci objektu User.
    Používá se typicky pro odpovědi API (GET požadavky).
    Nezahrnuje citlivá data jako heslo.
    """
    # `dump_only=True`: Toto pole bude zahrnuto pouze při serializaci (dumping) objektu na JSON.
    # Nebude očekáváno ani zpracováno při deserializaci (loading) dat z požadavku.
    # Typicky se používá pro ID a generovaná pole (jako created_at).
    id = fields.Int(dump_only=True)

    # `required=True`: Toto pole je povinné při deserializaci (pokud by se toto schéma použilo pro vstup).
    # Při serializaci musí mít objekt odpovídající atribut.
    username = fields.Str(required=True, validate=validate.Length(min=3))
    # `validate=validate.Length(min=3)`: Přidává validační pravidlo - řetězec musí mít minimálně 3 znaky.

    # `fields.Email`: Speciální typ pole, který automaticky validuje formát emailové adresy.
    email = fields.Email(required=True)

    # `dump_only=True`: Datum vytvoření je generováno serverem/databází, takže ho jen vracíme v odpovědi.
    created_at = fields.DateTime(dump_only=True)


class UserCreateSchema(Schema):
    """
    Schéma specificky navržené pro deserializaci a validaci dat
    při vytváření nového uživatele (POST požadavek).
    Může se lišit od UserSchema (např. může obsahovat pole pro heslo).
    """
    # Pole jsou stejná jako v UserSchema, protože pro vytvoření potřebujeme username a email.
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)

    # `load_only=True`: Toto pole bude očekáváno a zpracováno POUZE při deserializaci (loading)
    # dat z požadavku (např. JSON z POST). Nebude nikdy zahrnuto v odpovědi API (dumping).
    # Ideální pro hesla nebo jiná data, která přijímáme, ale nechceme je posílat zpět.
    # password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8)) # Příklad s validací délky hesla


# --- Schémata pro další modely ---
# Zde přidejte schémata pro vaše další modely (Event, Registration, atd.)

# class EventSchema(Schema):
#     """Schéma pro serializaci a základní validaci události."""
#     id = fields.Int(dump_only=True)
#     name = fields.Str(required=True, validate=validate.Length(min=5))
#     date = fields.Date(required=True)
#     description = fields.Str() # Popis může být nepovinný
#     created_at = fields.DateTime(dump_only=True)

# class EventCreateSchema(Schema):
#     """Schéma pro vytváření nové události."""
#     name = fields.Str(required=True, validate=validate.Length(min=5))
#     date = fields.Date(required=True)
#     description = fields.Str()

# class RegistrationSchema(Schema):
#     """Schéma pro serializaci registrace."""
#     id = fields.Int(dump_only=True)
#     user_id = fields.Int(required=True) # Můžeme nechat jen ID nebo vnořit UserSchema
#     event_id = fields.Int(required=True) # Můžeme nechat jen ID nebo vnořit EventSchema
#     registration_time = fields.DateTime(dump_only=True)
#     status = fields.Str(dump_only=True) # Status typicky nastavuje logika aplikace

    # Příklad vnořeného schématu (pokud chceme v odpovědi celé objekty User a Event):
    # user = fields.Nested(UserSchema, dump_only=True)
    # event = fields.Nested(EventSchema, dump_only=True)

# class RegistrationCreateSchema(Schema):
#      """Schéma pro vytvoření nové registrace."""
#      # Typicky potřebujeme jen ID uživatele a události, které přijdou v požadavku
#      user_id = fields.Int(required=True, load_only=True)
#      event_id = fields.Int(required=True, load_only=True)
