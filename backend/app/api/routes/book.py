# Základní třída pro pohledy založené na třídách.
from flask.views import MethodView
# Funkce pro generování HTTP chybových odpovědí.
from flask_jwt_extended import jwt_required
from flask_smorest import abort, Blueprint

# Import instance SQLAlchemy databáze.
from app.db import db
# Import databázových modelů Book, Author, Publisher.
from app.models import Book, Author, Publisher
# Import Marshmallow schémat pro knihy.
from app.schemas import BookSchema, BookCreateSchema, BookUpdateSchema
# Výjimka pro odchytávání chyb databázové integrity.
from sqlalchemy.exc import IntegrityError

from app.utils.auth_decorator import access_control

# --- Endpointy pro knihy ---

book_bp = Blueprint("books", __name__, url_prefix="/books",
                    description="Endpointy pro správu knihy")


@book_bp.route("/")
class BooksResource(MethodView):
    """
    Resource pro operace s kolekcí knih.
    Resource pro operace s kolekcí knih (/books).
    Zpracovává GET (seznam) a POST (vytvoření).
    """

    # GET /books: Vrátí seznam všech knih.
    # Odpověď bude HTTP 200 s polem objektů serializovaných pomocí BookSchema.
    @book_bp.response(200, BookSchema(many=True))
    @access_control()
    def get(self):
        """Získat seznam všech knih."""
        # Dotaz na všechny knihy, seřazené podle názvu.
        stmt = db.select(Book).order_by(Book.title)
        books = db.session.scalars(stmt).all()
        return books

    # POST /books: Vytvoří novou knihu.
    # Očekává data v těle požadavku validovaná pomocí BookCreateSchema.
    @book_bp.arguments(BookCreateSchema)
    # Úspěšná odpověď bude HTTP 201 s nově vytvořenou knihou serializovanou pomocí BookSchema.
    @book_bp.response(201, BookSchema)
    def post(self, new_book_data):
        """
        Vytvořit novou knihu.
        Očekává data podle BookCreateSchema v těle POST požadavku.
        """
        # Z new_book_data (slovník z validovaného JSONu) získáme ID autorů a ID vydavatele.
        # .pop() odstraní klíč ze slovníku a vrátí jeho hodnotu (nebo default, pokud není přítomen).
        # To je důležité, protože atributy 'author_ids' a 'publisher_id' nejsou přímo atributy modelu Book.
        author_ids = new_book_data.pop("author_ids", [])
        publisher_id_val = new_book_data.pop("publisher_id", None)

        isbn_to_check = new_book_data.get("isbn")
        if isbn_to_check:
            stmt = db.select(Book).where(Book.isbn == isbn_to_check)
            existing_book_isbn = db.session.scalars(stmt).first()
            # Pokud kniha s daným ISBN již existuje, vrátí chybu 409 Conflict.
            if existing_book_isbn:
                abort(
                    409, message=f"Kniha s ISBN '{isbn_to_check}' již existuje.")

        # Vytvoření instance modelu Book ze zbývajících dat v new_book_data.
        book = Book(**new_book_data)

        # Přiřazení vydavatele, pokud bylo jeho ID poskytnuto.
        if publisher_id_val is not None:
            publisher = db.session.get(Publisher, publisher_id_val)
            # Pokud vydavatel s daným ID neexistuje, vrátí chybu 400 Bad Request.
            if not publisher:
                abort(
                    400, message=f"Vydavatel s ID {publisher_id_val} neexistuje.")
            book.publisher = publisher

        # Přiřazení autorů, pokud byla jejich ID poskytnuta.
        if author_ids:
            authors_list = []
            for author_id in author_ids:
                author = db.session.get(Author, author_id)
                # Pokud některý z autorů s daným ID neexistuje, vrátí chybu 400 Bad Request.
                if not author:
                    abort(400, message=f"Autor s ID {author_id} neexistuje.")
                authors_list.append(author)
            book.authors = authors_list

        try:
            db.session.add(book)
            # Změny (včetně přiřazení autorů a vydavatele přes relationships)
            # se uloží do databáze.
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            # Chyba integrity může nastat i z jiných důvodů (např. unikátní omezení na modelu Book).
            abort(
                409,
                message="Chyba při ukládání: Kniha s těmito údaji (např. ISBN) již pravděpodobně existuje nebo došlo k porušení integrity dat.",
            )
        except Exception as e:
            db.session.rollback()
            # Obecná chyba serveru.
            abort(
                500, message=f"Interní chyba serveru při ukládání knihy: {str(e)}")

        return book


@book_bp.route("/<int:book_id>")
class BookResource(MethodView):
    """
    Resource pro operace s konkrétní knihou, identifikovanou pomocí ID.
    Resource pro operace s konkrétní knihou (/books/<id>).
    Zpracovává GET (detail), PUT (aktualizace), DELETE (smazání).
    """

    # GET /books/<book_id>: Vrátí detail knihy.
    @book_bp.response(200, BookSchema)
    def get(self, book_id):
        """Získat detail knihy podle ID."""
        book = db.session.get(Book, book_id)
        if book is None:
            # Pokud kniha neexistuje, vrátí 404 Not Found.
            abort(404, message="Kniha nebyla nalezena.")
        return book

    # PUT /books/<book_id>: Aktualizuje existující knihu.
    # Očekává data validovaná pomocí BookUpdateSchema.
    @book_bp.arguments(BookUpdateSchema)
    # Úspěšná odpověď bude HTTP 200 s aktualizovanou knihou.
    @book_bp.response(200, BookSchema)
    def put(self, update_data, book_id):
        """
        Aktualizovat existující knihu.
        Očekává data podle BookUpdateSchema v těle PUT požadavku.
        """
        book = db.session.get(Book, book_id)
        if book is None:
            abort(404, message="Kniha nebyla nalezena.")

        # Zpracování aktualizace ID vydavatele, pokud je přítomno v datech.
        if "publisher_id" in update_data:
            publisher_id_val = update_data.pop("publisher_id")
            if publisher_id_val is None:
                # Pokud je publisher_id None, odstraní se vazba na vydavatele.
                book.publisher = None
            else:
                # Jinak se načte nový vydavatel a přiřadí se knize.
                publisher = db.session.get(Publisher, publisher_id_val)
                if not publisher:
                    abort(
                        400, message=f"Vydavatel s ID {publisher_id_val} neexistuje.")
                book.publisher = publisher

        if "author_ids" in update_data:
            # Zpracování aktualizace seznamu ID autorů.
            author_ids_val = update_data.pop(
                "author_ids")
            new_authors_list = []
            if author_ids_val:
                # Sestavení nového seznamu objektů Author.
                for author_id in author_ids_val:
                    author = db.session.get(Author, author_id)
                    # Pokud některý autor neexistuje, vrátí chybu.
                    if not author:
                        abort(
                            400, message=f"Autor s ID {author_id} neexistuje.")
                    new_authors_list.append(author)
            book.authors = new_authors_list

        new_isbn = update_data.get("isbn")
        # Pokud se aktualizuje ISBN, zkontroluje se jeho unikátnost (nesmí patřit jiné knize).
        if new_isbn and new_isbn != book.isbn:
            stmt = db.select(Book).where(
                Book.isbn == new_isbn, Book.book_id != book_id)
            existing_book_isbn = db.session.scalars(stmt).first()
            if existing_book_isbn:
                # Pokud ISBN již používá jiná kniha, vrátí chybu 409 Conflict.
                abort(409, message=f"Kniha s ISBN '{new_isbn}' již existuje.")

        # Aktualizace ostatních atributů knihy na základě zbývajících dat v update_data.
        for key, value in update_data.items():
            setattr(book, key, value)

        # Uložení všech změn do databáze.
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            abort(
                409,
                message="Chyba při aktualizaci: Údaje (např. ISBN) kolidují s existující knihou nebo došlo k porušení integrity dat.",
            )
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"Interní chyba serveru při aktualizaci knihy: {str(e)}")

        return book

    # DELETE /books/<book_id>: Smaže knihu.
    # Úspěšná odpověď bude HTTP 204 No Content.
    @book_bp.response(204)
    def delete(self, book_id):
        """Smazat knihu podle ID."""
        book = db.session.get(Book, book_id)
        if book is None:
            # Pokud kniha neexistuje, vrátí 404 Not Found.
            abort(404, message="Kniha nebyla nalezena.")

        try:
            db.session.delete(book)
            # Potvrzení smazání v databázi.
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            abort(
                500, message=f"Interní chyba serveru při mazání knihy: {str(e)}")

        return ""
