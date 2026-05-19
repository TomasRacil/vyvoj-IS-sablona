from app import db
from .book_author_table import book_author_table

# --- Model pro autory (Authors) ---


from sqlalchemy.dialects.postgresql import UUID
import uuid

class Author(db.Model):
    """
    Model reprezentující autora knih.
    Vztah M:N s knihami (autor může napsat více knih, kniha může mít více autorů).
    """

    __tablename__ = "authors"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)

    # Definice vztahu M:N k tabulce 'books' pomocí asociační tabulky 'book_authors_table'
    books = db.relationship(
        "Book", secondary=book_author_table, lazy="dynamic", back_populates="authors"
    )

    def __repr__(self):
        return f"<Author(author_id={self.author_id}, name='{self.first_name} {self.last_name}')>"
