# Základní třída pro pohledy založené na třídách
from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required, decode_token
# Funkce pro HTTP chyby a Blueprint z Flask-Smorest
from flask_smorest import abort, Blueprint

# Importy z vaší aplikace
from app.models import User, Role  # Import databázových modelů
# Import Marshmallow schémat
from app.models.token_blacklist import TokenBlacklist
from app.schemas import (
    UserLoginSchema, UserCreateSchema, UserSchema,
    RoleSchema, UserRoleAssignSchema
)
from app.db import db  # Import instance SQLAlchemy databáze
from sqlalchemy.exc import IntegrityError  # Pro odchytávání chyb unikátnosti
from sqlalchemy import or_
from app.utils.auth_decorator import access_control  # Dekorátor pro řízení přístupu
from app.utils.enums import UserRoleEnum  # Enum pro role


auth_bp = Blueprint("auth", __name__, url_prefix="/auth",
                    description="Blueprint zajišťující auth operace")


@auth_bp.route("/login")
class UserLogin(MethodView):
    @auth_bp.arguments(UserLoginSchema)
    def post(self, user_data):
        """Přihlásí uživatele a vrátí JWT tokeny."""
        login_identifier = user_data["username_or_email"]
        password = user_data["password"]

        user = db.session.execute(
            db.select(User).where(
                or_(User.username == login_identifier,
                    User.email == login_identifier)
            )
        ).scalar_one_or_none()

        if user and user.check_password(password):
            # Identita pro JWT může být ID uživatele
            refresh_token_string = create_refresh_token(
                identity=user.id)  # Volitelný refresh token

            # Získáme JTI z refresh tokenu, abychom ho mohli přidat do access tokenu
            decoded_refresh_token = decode_token(refresh_token_string)
            refresh_jti = decoded_refresh_token['jti']

            access_token = create_access_token(identity=str(
                user.id), additional_claims={"refresh_jti": refresh_jti})
            return jsonify(access_token=access_token, refresh_token=refresh_token_string), 200

        abort(401, message="Nesprávné uživatelské jméno/email nebo heslo.")


@auth_bp.route("/logout", methods=["POST"])
class UserLogout(MethodView):
    """
    Resource pro odhlášení uživatele (blacklistování JWT).
    """

    @jwt_required()
    def post(self):
        """
        Odhlásí uživatele přidáním JTI aktuálního access tokenu na blacklist
        a také JTI souvisejícího refresh tokenu, pokud je nalezen v claims access tokenu.
        """
        current_token_payload = get_jwt()
        access_jti = current_token_payload["jti"]
        # Získáme JTI refresh tokenu z claimu
        refresh_jti_from_claim = current_token_payload.get("refresh_jti")

        try:
            blacklisted_tokens = []

            # Přidání JTI access tokenu na blacklist
            token_blacklist_entry_access = TokenBlacklist(jti=access_jti)
            blacklisted_tokens.append(token_blacklist_entry_access)

            # Přidání JTI refresh tokenu na blacklist, pokud existuje
            if refresh_jti_from_claim:
                token_blacklist_entry_refresh = TokenBlacklist(
                    jti=refresh_jti_from_claim)
                blacklisted_tokens.append(token_blacklist_entry_refresh)

            db.session.add_all(blacklisted_tokens)
            db.session.commit()

            message = "Úspěšně odhlášeno. Access token byl zneplatněn."
            if refresh_jti_from_claim:
                message = "Úspěšně odhlášeno. Access token i související refresh token byly zneplatněny."
            return jsonify(message=message), 200
        except Exception as e:
            db.session.rollback()
            # Zde by mělo být logování chyby 'e'
            abort(500, message="Interní chyba serveru při odhlašování.")


@auth_bp.route("/register")
class UserRegisterResource(MethodView):
    """
    Resource pro registraci nových uživatelů.
    """

    @auth_bp.arguments(UserCreateSchema)
    # Dekorátor definuje očekávaná vstupní data v těle požadavku.
    # - UserCreateSchema: Určuje Marshmallow schéma pro validaci vstupních dat.
    # - Pokud validace selže, automaticky vrátí chybu 422 Unprocessable Entity.
    # - Validovaná data jsou předána jako argument metody (zde 'new_user_data').
    @auth_bp.response(201, UserSchema)
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
        user = User(
            username=new_user_data["username"],
            email=new_user_data["email"]
        )
        # Heslo se hash_old_defaultuje přes setter
        user.password = new_user_data["password"]

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


@auth_bp.route("/refresh", methods=["POST"])
class TokenRefresh(MethodView):
    """
    Resource pro obnovení access tokenu pomocí refresh tokenu.
    """
    @access_control(refresh=True)
    def post(self):
        """
        Obnoví access token.
        Očekává platný refresh token v Authorization hlavičce (Bearer token).
        """
        current_user_identity = get_jwt_identity()
        # Získáme JTI z aktuálního refresh tokenu (payload je již dekódovaný díky @jwt_required)
        current_refresh_token_payload = get_jwt()
        refresh_jti = current_refresh_token_payload['jti']

        new_access_token = create_access_token(
            identity=current_user_identity, additional_claims={"refresh_jti": refresh_jti})
        return jsonify(access_token=new_access_token), 200


@auth_bp.route("/<uuid:user_id>/roles")
class UserRolesManagementResource(MethodView):
    """
    Resource pro správu rolí konkrétního uživatele.
    Vyžaduje administrátorská práva.
    """

    @auth_bp.arguments(UserRoleAssignSchema)
    @auth_bp.response(200, UserSchema)  # Vrátí aktualizovaného uživatele
    @access_control(required_roles=[UserRoleEnum.ADMIN])
    def post(self, role_data, user_id):
        """
        Přiřadit roli uživateli.
        """
        user = db.session.get(User, user_id)
        if not user:
            abort(404, message="Uživatel nebyl nalezen.")

        role_id_to_assign = role_data["role_id"]
        role = db.session.get(Role, role_id_to_assign)
        if not role:
            abort(
                404, message=f"Role s ID {role_id_to_assign} nebyla nalezena.")

        if role not in user.roles.all():  # user.roles je lazy='dynamic'
            user.roles.append(role)
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Zde by mělo být logování chyby 'e'
                abort(500, message="Interní chyba serveru při přiřazování role.")
        # Pokud uživatel roli již má, neprovádíme žádnou akci, vrátíme aktuální stav uživatele.
        return user

    @auth_bp.response(200, RoleSchema(many=True))
    # @access_control(required_roles=[UserRoleEnum.ADMIN])
    def get(self, user_id):
        """
        Získat všechny role konkrétního uživatele.
        """
        user = db.session.get(User, user_id)
        if not user:
            abort(404, message="Uživatel nebyl nalezen.")
        return user.roles.all()  # .all() protože user.roles je lazy='dynamic'


@auth_bp.route("/<uuid:user_id>/roles/<int:role_id>")
class UserRoleDetailManagementResource(MethodView):
    """
    Resource pro odebrání konkrétní role uživateli.
    Vyžaduje administrátorská práva.
    """
    @auth_bp.response(204)
    # @access_control(required_roles=[UserRoleEnum.ADMIN])
    def delete(self, user_id, role_id):
        """
        Odebrat roli uživateli.
        """
        user = db.session.get(User, user_id)
        if not user:
            abort(404, message="Uživatel nebyl nalezen.")

        role_to_remove = user.roles.filter(Role.id == role_id).first()
        if not role_to_remove:
            abort(
                404, message=f"Uživatel nemá přiřazenou roli s ID {role_id} nebo role neexistuje.")

        user.roles.remove(role_to_remove)
        db.session.commit()
        return ""
