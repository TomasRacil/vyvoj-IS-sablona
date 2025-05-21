from app import db
from sqlalchemy.dialects.postgresql import UUID  # Pro typ UUID v PostgreSQL

# --- Asociační tabulka pro vztah M:N mezi Users a Roles ---
user_roles_table = db.Table(
    "user_roles",
    db.metadata,
    db.Column(
        "user_id",
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    ),
    db.Column(
        "role_id",
        db.Integer,
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True
    )
)
