from app import db  # Import instance SQLAlchemy z db.py
from sqlalchemy.sql import func  # Import SQL funkcí (např. pro server_default)
from sqlalchemy.dialects.postgresql import UUID  # Pro typ UUID v PostgreSQL
from passlib.hash import pbkdf2_sha256 as sha256
import uuid  # Pro generování UUID
from .user_roles_table import user_roles_table  # Import asociační tabulky
# from .role import Role # Import modelu Role - lze použít stringový odkaz v relationship

# from werkzeug.security import generate_password_hash, check_password_hash # Příklad pro hashování hesel

# Model pro uživatele (User)


class User(db.Model):
    """
    Model reprezentující uživatele v informačním systému.
    """

    # Explicitní pojmenování tabulky v databázi - dobrá praxe
    __tablename__ = "users"

    # Primární klíč - UUID
    # Používáme UUID(as_uuid=True) aby SQLAlchemy pracovalo s Python uuid objekty
    # default=uuid.uuid4 zajistí generování nového UUID při vytvoření záznamu
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Sloupec pro uživatelské jméno (řetězec, max 80 znaků, unikátní, povinný)
    username = db.Column(db.String(80), unique=True, nullable=False)

    # Sloupec pro email (řetězec, max 120 znaků, unikátní, povinný)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Sloupec pro datum a čas vytvoření záznamu s časovou zónou
    # server_default=func.now() zajistí automatické nastavení času databázovým serverem
    # při vytvoření záznamu. To je obecně preferovanější než `default=datetime.utcnow`.
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    # Heslo by mělo být povinné
    password_hash = db.Column(db.String(128), nullable=False)

    # Vztah M:N k rolím
    # 'Role' je název třídy modelu na druhé straně vztahu.
    # secondary=user_roles_table určuje asociační tabulku.
    # back_populates='users' propojuje tento vztah s atributem 'users' v modelu Role.
    # lazy='dynamic' umožňuje další filtrování/řazení před načtením dat.
    roles = db.relationship("Role", secondary=user_roles_table,
                            back_populates="users", lazy="dynamic")

    @property
    def password(self):
        # Heslo by se nemělo číst přímo
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = sha256.hash(password)

    def check_password(self, password):
        return sha256.verify(password, self.password_hash)

    def has_role(self, role_name_or_enum):
        """
        Kontroluje, zda má uživatel danou roli.
        :param role_name_or_enum: Název role (string) nebo člen UserRoleEnum.
        """
        from app.utils.enums import UserRoleEnum  # Lokální import pro Enum
        if isinstance(role_name_or_enum, UserRoleEnum):
            role_name = role_name_or_enum.value
        else:
            role_name = str(role_name_or_enum)

        # Použijeme .filter() pro dotaz do DB. Pro jednoduchou kontrolu existence je any() efektivní.
        return self.roles.filter_by(name=role_name).first() is not None

    # Metoda pro reprezentaci objektu jako řetězce (užitečné pro ladění)
    def __repr__(self):
        return f"<User {self.username}>"
