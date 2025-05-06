from app import db

# --- Asociační tabulka pro vztah M:N mezi Books a Authors ---
# Definuje se pomocí db.Table, protože neobsahuje žádná další data kromě cizích klíčů.
book_author_table = db.Table(
    "books_authors",
    db.metadata,
    db.Column(
        "book_id",
        db.Integer,
        db.ForeignKey("books.book_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "author_id",
        db.Integer,
        db.ForeignKey("authors.author_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    # ondelete='CASCADE' zajistí, že pokud je smazána kniha nebo autor,
    # smaže se i odpovídající záznam v této propojovací tabulce.
)
