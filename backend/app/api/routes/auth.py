# Základní třída pro pohledy založené na třídách
from flask import jsonify
from flask.views import MethodView
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, jwt_required
from flask_smorest import abort  # Funkce pro HTTP chyby a Blueprint z Flask-Smorest

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
from app.api import api_v1_bp
from sqlalchemy import or_
from app.utils.auth_decorator import access_control  # Dekorátor pro řízení přístupu
from app.utils.enums import UserRoleEnum  # Enum pro role


@api_v1_bp.route("/login")
class UserLogin(MethodView):
    @api_v1_bp.arguments(UserLoginSchema)
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
            access_token = create_access_token(identity=str(user.id))
            refresh_token = create_refresh_token(
                identity=user.id)  # Volitelný refresh token
            return jsonify(access_token=access_token, refresh_token=refresh_token), 200

        abort(401, message="Nesprávné uživatelské jméno/email nebo heslo.")


@api_v1_bp.route("/logout", methods=["POST"])
class UserLogout(MethodView):
    """
    Resource pro odhlášení uživatele (blacklistování JWT).
    """
    # @access_control()  # Vyžaduje platný access token

    def post(self):
        """
        Odhlásí uživatele přidáním JTI aktuálního tokenu na blacklist.
        """
        jti = get_jwt()["jti"]
        try:
            token_blacklist_entry = TokenBlacklist(jti=jti)
            db.session.add(token_blacklist_entry)
            db.session.commit()
            return jsonify(message="Úspěšně odhlášeno."), 200
        except Exception as e:
            db.session.rollback()
            abort(500, message="Interní chyba serveru při odhlašování.")


@api_v1_bp.route("/register")
class UserRegisterResource(MethodView):
    """
    Resource pro registraci nových uživatelů.
    """

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


@api_v1_bp.route("/users/<uuid:user_id>/roles")
class UserRolesManagementResource(MethodView):
    """
    Resource pro správu rolí konkrétního uživatele.
    Vyžaduje administrátorská práva.
    """

    @api_v1_bp.arguments(UserRoleAssignSchema)
    @api_v1_bp.response(200, UserSchema)  # Vrátí aktualizovaného uživatele
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

    @api_v1_bp.response(200, RoleSchema(many=True))
    # @access_control(required_roles=[UserRoleEnum.ADMIN])
    def get(self, user_id):
        """
        Získat všechny role konkrétního uživatele.
        """
        user = db.session.get(User, user_id)
        if not user:
            abort(404, message="Uživatel nebyl nalezen.")
        return user.roles.all()  # .all() protože user.roles je lazy='dynamic'


@api_v1_bp.route("/users/<uuid:user_id>/roles/<int:role_id>")
class UserRoleDetailManagementResource(MethodView):
    """
    Resource pro odebrání konkrétní role uživateli.
    Vyžaduje administrátorská práva.
    """
    @api_v1_bp.response(204)
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
