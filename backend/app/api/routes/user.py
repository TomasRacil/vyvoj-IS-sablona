# Základní třída pro pohledy založené na třídách
from flask.views import MethodView
# Funkce pro HTTP chyby a Blueprint z Flask-Smorest
from flask_smorest import abort, Blueprint

# Importy z vaší aplikace
from app.models import User  # Import databázového modelů User
# Import Marshmallow schémat
from app.schemas import UserCreateSchema, UserSchema, RoleSchema, UserRoleAssignSchema
from app.db import db  # Import instance SQLAlchemy databáze
from sqlalchemy.exc import IntegrityError  # Pro odchytávání chyb unikátnosti
from app.utils.auth_decorator import access_control
from app.utils.enums import UserRoleEnum  # Enum pro role

# --- Endpointy pro uživatele ---

user_bp = Blueprint("users", __name__, url_prefix="/users",
                    description="Blueprint zajišťující operace s uživateli")


# Dekorátor registruje třídu pro danou cestu na blueprintu
@user_bp.route("/")
class UsersResource(MethodView):
    """
    Resource pro operace s kolekcí uživatelů (/users).
    Zpracovává GET (seznam) a POST (vytvoření).
    """

    @user_bp.response(200, UserSchema(many=True))
    @access_control(required_roles=[UserRoleEnum.ADMIN])
    def get(self):
        """Získat seznam všech uživatelů."""
        stmt = db.select(User).order_by(User.username)
        users = db.session.scalars(stmt).all()
        return users


@user_bp.route("/me")
class UserMeResource(MethodView):
    """
    Resource pro získání informací o aktuálně přihlášeném uživateli.
    """

    @user_bp.response(200, UserSchema)
    @access_control()
    def get(self):
        """Získat profil aktuálně přihlášeného uživatele."""
        from flask_jwt_extended import get_jwt_identity
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if user is None:
            abort(404, message="Uživatel nebyl nalezen.")
        return user


@user_bp.route("/<uuid:user_id>")  # Změna typu user_id na uuid
class UserResource(MethodView):
    """
    Resource pro operace s konkrétním uživatelem (/users/<id>).
    Zpracovává GET (detail), PUT (aktualizace), DELETE (smazání).
    """

    @user_bp.response(200, UserSchema)
    @access_control(required_roles=[UserRoleEnum.ADMIN], allow_owner=True, owner_id_param_name="user_id")
    def get(self, user_id):
        """Získat detail uživatele podle ID."""
        # Použití metody get_or_404 pro snadné získání záznamu nebo vrácení 404 Not Found
        user = db.session.get(User, user_id)  # Moderní způsob získání podle PK
        if user is None:
            abort(404, message="Uživatel nebyl nalezen.")
        # Alternativa: user = User.query.get_or_404(user_id, description="Uživatel nebyl nalezen.")
        return user

    @user_bp.arguments(
        UserSchema
    )  # Předpokládáme UserSchema pro update, možná budete chtít UserUpdateSchema
    @user_bp.response(200, UserSchema)
    @access_control(required_roles=[UserRoleEnum.ADMIN], allow_owner=True, owner_id_param_name="user_id")
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

    @user_bp.response(204)  # Odpověď HTTP 204 No Content pro úspěšné smazání
    @access_control(required_roles=[UserRoleEnum.ADMIN])
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
