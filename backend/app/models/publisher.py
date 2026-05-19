# --- Model pro vydavatele (Publishers) ---
from app import db


from sqlalchemy.dialects.postgresql import UUID
import uuid

class Publisher(db.Model):
    """
    Model reprezentující vydavatele knih.
    Vztah 1:N s knihami (jeden vydavatel může vydat více knih).
    """

    __tablename__ = "publishers"  # Explicitní název tabulky v databázi

    # Primární klíč
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Název vydavatele
    name = db.Column(db.String(100), unique=True, nullable=False)
    # Sídlo vydavatele
    address = db.Column(db.String(200), nullable=True)

    # Definice vztahu 1:N k tabulce 'books'
    books = db.relationship("Book", back_populates="publisher", lazy="dynamic")

    # Metoda pro reprezentaci objektu jako řetězce (užitečné pro ladění)
    def __repr__(self):
        return f"<Publisher(publisher_id={self.publisher_id}, name='{self.name}')>"
