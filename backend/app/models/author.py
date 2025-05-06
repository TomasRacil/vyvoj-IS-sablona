from app import db
from .book_author_table import book_author_table

# --- Model pro autory (Authors) ---


class Author(db.Model):
    """
    Model reprezentující autora knih.
    Vztah M:N s knihami (autor může napsat více knih, kniha může mít více autorů).
    """

    __tablename__ = "authors"

    author_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_year = db.Column(
        db.Integer, nullable=True
    )  # CHECK constraint (birth_year > 0) definujeme v migraci

    # Definice vztahu M:N k tabulce 'books' pomocí asociační tabulky 'book_authors_table'
    # secondary=book_authors_table určuje, která tabulka se použije pro propojení.
    # back_populates='authors' propojuje tento vztah s atributem 'authors' v modelu Book.
    # lazy='dynamic' umožňuje další filtrování načtených knih.
    books = db.relationship(
        "Book", secondary=book_author_table, lazy="dynamic", back_populates="authors"
    )

    def __repr__(self):
        return f"<Author(author_id={self.author_id}, name='{self.first_name} {self.last_name}')>"
