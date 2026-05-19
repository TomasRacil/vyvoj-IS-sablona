from app import db
from .book_author_table import book_author_table
from sqlalchemy.dialects.postgresql import UUID
import uuid

# --- Model pro knihy (Books) ---

class Book(db.Model):
    """
    Model reprezentující knihu.
    Vztah N:1 s vydavatelem (kniha má jednoho vydavatele).
    Vztah M:N s autory (kniha může mít více autorů).
    """

    __tablename__ = "books"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = db.Column(db.String(200), nullable=False)
    published_year = db.Column(db.Integer, nullable=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True)

    # Cizí klíč na vydavatele
    publisher_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("publishers.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )

    # Vztah N:1 k tabulce 'publishers'
    publisher = db.relationship("Publisher", back_populates="books")

    # Vztah M:N k tabulce 'authors'
    authors = db.relationship(
        "Author", secondary=book_author_table, lazy="dynamic", back_populates="books"
    )

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}')>"
