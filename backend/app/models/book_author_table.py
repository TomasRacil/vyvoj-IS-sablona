from app import db

from sqlalchemy.dialects.postgresql import UUID

# --- Asociační tabulka pro vztah M:N mezi Books a Authors ---
book_author_table = db.Table(
    "book_authors",
    db.metadata,
    db.Column(
        "book_id",
        UUID(as_uuid=True),
        db.ForeignKey("books.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "author_id",
        UUID(as_uuid=True),
        db.ForeignKey("authors.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
