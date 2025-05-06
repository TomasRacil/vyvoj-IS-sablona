# --- Model pro vydavatele (Publishers) ---
from app import db


class Publisher(db.Model):
    """
    Model reprezentující vydavatele knih.
    Vztah 1:N s knihami (jeden vydavatel může vydat více knih).
    """

    __tablename__ = "publishers"  # Explicitní název tabulky v databázi

    # Primární klíč (automaticky se generuje jako SERIAL v PostgreSQL)
    publisher_id = db.Column(db.Integer, primary_key=True)
    # Název vydavatele - textový řetězec, max 100 znaků, musí být unikátní a nesmí být NULL
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Sídlo vydavatele - delší text, může být NULL
    headquarters = db.Column(db.Text, nullable=True)

    # Definice vztahu 1:N k tabulce 'books'
    # 'Book' je název třídy modelu na druhé straně vztahu.
    # back_populates='publisher' propojuje tento vztah s atributem 'publisher' v modelu Book.
    # lazy='dynamic' znamená, že atribut 'books' vrátí objekt dotazu (query object),
    # který lze dále filtrovat/řadit, než se reálně načtou data z DB.
    books = db.relationship("Book", back_populates="publisher", lazy="dynamic")

    # Metoda pro reprezentaci objektu jako řetězce (užitečné pro ladění)
    def __repr__(self):
        return f"<Publisher(publisher_id={self.publisher_id}, name='{self.name}')>"
