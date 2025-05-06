from app import db
from .book_author_table import book_author_table

# --- Model pro knihy (Books) ---


class Book(db.Model):
    """
    Model reprezentující knihu.
    Vztah N:1 s vydavatelem (kniha má jednoho vydavatele).
    Vztah M:N s autory (kniha může mít více autorů).
    """

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    publication_year = db.Column(
        db.Integer, nullable=True
    )  # CHECK constraint v migraci
    # ISBN by mělo být unikátní, pokud je zadáno
    isbn = db.Column(db.String(13), unique=True, nullable=True)
    # Počet stran (musí být kladný) - CHECK constraint v migraci
    page_count = db.Column(db.Integer, nullable=True)
    # Cena (max 999999.99, nesmí být záporná) - CHECK constraint v migraci
    price = db.Column(db.Numeric(8, 2), nullable=True)

    # Cizí klíč na vydavatele
    # ondelete='SET NULL' zajistí, že pokud je vydavatel smazán,
    # hodnota publisher_id v této knize se nastaví na NULL (pokud to sloupec povoluje).
    # onupdate='CASCADE' zajistí, že pokud se změní ID vydavatele, změní se i zde.
    publisher_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "publishers.publisher_id", ondelete="SET NULL", onupdate="CASCADE"
        ),
        nullable=True,
    )

    # Vztah N:1 k tabulce 'publishers' (propojeno přes back_populates='books' v modelu Publisher)
    publisher = db.relationship("Publisher", back_populates="books")

    # Vztah M:N k tabulce 'authors' (propojeno přes back_populates='books' v modelu Author)
    authors = db.relationship(
        "Author", secondary=book_author_table, lazy="dynamic", back_populates="books"
    )

    def __repr__(self):
        return f"<Book(book_id={self.book_id}, title='{self.title}')>"
