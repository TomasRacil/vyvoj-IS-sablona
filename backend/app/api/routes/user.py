# Základní třída pro pohledy založené na třídách
from flask.views import MethodView
from flask_smorest import abort  # Funkce pro HTTP chyby a Blueprint z Flask-Smorest

# Importy z vaší aplikace
from app.models import User, Role  # Import databázových modelů User a Role
# Import Marshmallow schémat
from app.schemas import UserCreateSchema, UserSchema, RoleSchema, UserRoleAssignSchema
from app.db import db  # Import instance SQLAlchemy databáze
from sqlalchemy.exc import IntegrityError  # Pro odchytávání chyb unikátnosti
from app.api import api_v1_bp
from app.utils.auth_decorator import access_control
from app.utils.enums import UserRoleEnum  # Enum pro role

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


@api_v1_bp.route("/users/<uuid:user_id>")  # Změna typu user_id na uuid
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
    @access_control(UserRoleEnum.EDITOR, True, "user_id")
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
