# Tento soubor definuje API endpointy pomocí Flask-Smorest.
# Flask-Smorest využívá Marshmallow schémata pro validaci a serializaci
# a MethodView pro strukturování endpointů.

# Základní třída pro pohledy založené na třídách
from flask.views import MethodView
from flask_smorest import abort  # Funkce pro HTTP chyby a Blueprint z Flask-Smorest

# Poznámka: Váš kód importuje Blueprint z . (api_v1_bp = Blueprint(...)), což je také v pořádku.
# Zde předpokládáme, že api_v1_bp je instance Blueprint definovaná v api/__init__.py

# Importy z vaší aplikace
from app.models import User  # Import databázového modelu User
from ..schemas import UserSchema, UserCreateSchema  # Import Marshmallow schémat
from ..db import db  # Import instance SQLAlchemy databáze
from sqlalchemy.exc import IntegrityError  # Pro odchytávání chyb unikátnosti
from . import api_v1_bp

# Tento kód předpokládá, že `api_v1_bp` již existuje (importováno z __init__.py)

# --- Endpointy pro uživatele ---


# Dekorátor registruje třídu pro danou cestu na blueprintu
@api_v1_bp.route("/users")
class UsersResource(MethodView):
    """
    Resource pro operace s kolekcí uživatelů (/users).
    Zpracovává GET (seznam) a POST (vytvoření).
    """

    @api_v1_bp.response(200, UserSchema(many=True))
    # Dekorátor definuje úspěšnou odpověď (HTTP 200 OK).
    # - UserSchema(many=True): Určuje, že odpověď bude seznam objektů,
    #   které budou serializovány pomocí UserSchema.
    # - Automaticky generuje dokumentaci pro OpenAPI (Swagger).
    def get(self):
        """Získat seznam všech uživatelů."""
        # Použití moderního stylu SQLAlchemy 2.0 pro dotazování
        stmt = db.select(User).order_by(User.username)
        # scalars() vrátí jednotlivé hodnoty (objekty User), all() je načte
        users = db.session.scalars(stmt).all()
        # Flask-Smorest se postará o serializaci pomocí UserSchema(many=True)
        return users

    @api_v1_bp.arguments(UserCreateSchema)
    # Dekorátor definuje očekávaná vstupní data v těle požadavku.
    # - UserCreateSchema: Určuje Marshmallow schéma pro validaci vstupních dat.
    # - Pokud validace selže, automaticky vrátí chybu 422 Unprocessable Entity.
    # - Validovaná data jsou předána jako argument metody (zde 'new_user_data').
    @api_v1_bp.response(201, UserSchema)
    # Dekorátor definuje úspěšnou odpověď pro vytvoření (HTTP 201 Created).
    # - UserSchema: Určuje, že odpověď bude jeden objekt serializovaný pomocí UserSchema.
    def post(self, new_user_data):
        """
        Vytvořit nového uživatele.
        Očekává data podle UserCreateSchema v těle POST požadavku.
        """
        # Kontrola, zda uživatel s daným emailem nebo username již neexistuje
        if User.query.filter(
            (User.username == new_user_data["username"])
            | (User.email == new_user_data["email"])
        ).first():
            abort(
                409, message="Uživatel s tímto jménem nebo emailem již existuje."
            )  # Conflict

        # Vytvoření instance modelu User z validovaných dat
        user = User(**new_user_data)

        # !!! DŮLEŽITÉ: Zde by mělo dojít k hashování hesla před uložením!
        # Např. pomocí knihovny passlib nebo werkzeug.security
        # user.set_password(new_user_data['password']) # Předpokládá metodu v modelu User

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:  # Specifická chyba pro porušení unikátnosti
            db.session.rollback()
            # Logování chyby by bylo vhodné
            # print(f"IntegrityError: {e}")
            abort(
                409,  # Conflict - lepší než 500, pokud jde o unikátnost
                message=f"Chyba při ukládání: Uživatel s těmito údaji již pravděpodobně existuje.",
            )
        except Exception as e:  # Obecná chyba pro jiné problémy
            db.session.rollback()
            # Logování chyby
            # print(f"Exception: {e}")
            abort(500, message="Interní chyba serveru při ukládání uživatele.")
        # Vrácení nově vytvořeného uživatele (serializace proběhne automaticky)
        return user


@api_v1_bp.route("/users/<int:user_id>")  # Cesta s parametrem user_id
class UserResource(MethodView):
    """
    Resource pro operace s konkrétním uživatelem (/users/<id>).
    Zpracovává GET (detail), PUT (aktualizace), DELETE (smazání).
    """

    @api_v1_bp.response(200, UserSchema)
    # Odpověď pro úspěšné nalezení (HTTP 200 OK), serializovaná UserSchema.
    def get(self, user_id):
        """Získat detail uživatele podle ID."""
        # Použití metody get_or_404 pro snadné získání záznamu nebo vrácení 404 Not Found
        user = db.session.get(User, user_id)  # Moderní způsob získání podle PK
        if user is None:
            abort(404, message="Uživatel nebyl nalezen.")
        # Alternativa: user = User.query.get_or_404(user_id, description="Uživatel nebyl nalezen.")
        return user

    @api_v1_bp.arguments(
        UserSchema
    )  # Předpokládáme UserSchema pro update, možná budete chtít UserUpdateSchema
    @api_v1_bp.response(200, UserSchema)
    def put(self, update_data, user_id):
        """
        Aktualizovat existujícího uživatele (celý záznam).
        Očekává data podle UserSchema v těle PUT požadavku.
        """
        user = db.session.get(User, user_id)
        if user is None:
            abort(404, message="Uživatel nebyl nalezen.")

        # Aktualizace atributů - pozor na heslo!
        # Heslo by se mělo aktualizovat pouze pokud je zadáno a mělo by být hashováno.
        # Je lepší mít samostatný endpoint pro změnu hesla nebo specifické schéma.
        for key, value in update_data.items():
            # Zabráníme přímému přepsání hesla, pokud není explicitně řešeno
            if key != "password":
                setattr(user, key, value)

        # Příklad aktualizace hesla, pokud je v datech a je neprázdné:
        # if 'password' in update_data and update_data['password']:
        #    user.set_password(update_data['password']) # Opět, nutné hashování

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message="Interní chyba serveru při aktualizaci uživatele.")
        return user

    @api_v1_bp.response(204)  # Odpověď HTTP 204 No Content pro úspěšné smazání
    def delete(self, user_id):
        """Smazat uživatele podle ID."""
        user = db.session.get(User, user_id)
        if user is None:
            abort(404, message="Uživatel nebyl nalezen.")

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(500, message="Interní chyba serveru při mazání uživatele.")

        # Při úspěšném smazání se vrací prázdná odpověď s kódem 204
        return ""


# Zde můžete přidat další Resources pro jiné části vašeho API
# např. Events, Registrations, atd.
# @api_v1_bp.route("/events")
# class EventsResource(MethodView): ...
