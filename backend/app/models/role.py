from app import db

# Importujte user_roles_table až po její definici, nebo použijte stringový odkaz
# from .user_roles_table import user_roles_table # Cyklická závislost, pokud importujeme zde


class Role(db.Model):
    """
    Model reprezentující uživatelskou roli.
    """
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    # Např. 'admin', 'editor'
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    # Vztah M:N k uživatelům bude definován pomocí back_populates v User modelu
    # a sekundární tabulky.
    users = db.relationship(
        "User",
        secondary="user_roles",  # Název tabulky jako string
        back_populates="roles",
        lazy="dynamic"
    )

    def __repr__(self):
        return f"<Role {self.name}>"
