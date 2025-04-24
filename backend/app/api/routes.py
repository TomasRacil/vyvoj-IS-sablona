from flask.views import MethodView
from flask_smorest import abort  # Pro standardizované HTTP chyby
from . import api_v1_bp  # Import blueprintu
from ..models import User  # Import modelu
from ..schemas import UserSchema, UserCreateSchema  # Import schémat
from ..db import db  # Import instance databáze


# Příklad API endpointu pro uživatele
@api_v1_bp.route("/users")
class UsersResource(MethodView):

    @api_v1_bp.response(
        200, UserSchema(many=True)
    )  # Dekorátor pro OpenAPI dokumentaci a serializaci odpovědi
    def get(self):
        """Získat seznam všech uživatelů."""
        # Použití SQLAlchemy 2.0 stylu pro select
        stmt = db.select(User).order_by(User.username)
        users = db.session.scalars(stmt).all()
        return users

    @api_v1_bp.arguments(UserCreateSchema)  # Dekorátor pro validaci vstupních dat
    @api_v1_bp.response(
        201, UserSchema
    )  # Dekorátor pro úspěšnou odpověď (status 201 Created)
    def post(self, new_user_data):
        """Vytvořit nového uživatele."""
        # Zde by měla být kontrola, zda uživatel již neexistuje
        user = User(**new_user_data)
        # Zde by mělo být hashování hesla před uložením
        try:
            db.session.add(user)
            db.session.commit()
        except (
            Exception
        ) as e:  # Obecná chyba, lepší specifikovat (např. IntegrityError)
            db.session.rollback()
            abort(
                500, message=f"Nelze uložit uživatele: {e}"
            )  # Použití abort pro chybu
        return user


@api_v1_bp.route("/users/<int:user_id>")
class UserResource(MethodView):

    @api_v1_bp.response(200, UserSchema)
    def get(self, user_id):
        """Získat detail uživatele podle ID."""
        # Použití get_or_404 pro snadné získání nebo vrácení 404
        user = db.get_or_404(User, user_id, description="Uživatel nebyl nalezen.")
        return user

    # Zde přidejte metody pro PUT (update) a DELETE
    # @api_v1_bp.arguments(UserSchema) # Pro update
    # @api_v1_bp.response(200, UserSchema)
    # def put(self, update_data, user_id): ...

    # @api_v1_bp.response(204) # No Content pro úspěšné smazání
    # def delete(self, user_id): ...


# Přidejte routy pro další zdroje (Events, Registrations, etc.)
