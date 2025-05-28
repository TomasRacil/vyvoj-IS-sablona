# Základní třída pro pohledy založené na třídách
from flask.views import MethodView
# Funkce pro generování HTTP chybových odpovědí
from flask_smorest import abort, Blueprint

# Import modelů a schémat
from app.models import Author  # Import databázového modelu Author
# Import Marshmallow schémat pro autora
from app.schemas import AuthorSchema, AuthorCreateSchema
from app.db import db  # Import instance SQLAlchemy databáze
# Výjimka pro odchytávání chyb databázové integrity
from sqlalchemy.exc import IntegrityError

# --- Endpointy pro autory ---

# Dekorátor registruje třídu pro danou cestu na blueprintu

author_bp = Blueprint("authors", __name__, url_prefix="/authors",
                      description="Blueprint zajišťující operace s autory")


@author_bp.route("/")
class AuthorsResource(MethodView):
    """
    Resource pro operace s kolekcí autorů (/authors).
    Zpracovává GET (seznam) a POST (vytvoření).
    """

    @author_bp.response(200, AuthorSchema(many=True))
    # Dekorátor definuje úspěšnou odpověď (HTTP 200 OK).
    # - AuthorSchema(many=True): Určuje, že odpověď bude seznam objektů,
    #   které budou serializovány pomocí AuthorSchema.
    # - Automaticky generuje dokumentaci pro OpenAPI (Swagger).
    def get(self):
        """Získat seznam všech autorů."""
        # Vytvoření dotazu pro výběr všech autorů, seřazených podle příjmení a poté jména.
        stmt = db.select(Author).order_by(Author.last_name, Author.first_name)
        # Provedení dotazu a načtení všech výsledků. scalars() vrátí objekty Author.
        authors = db.session.scalars(stmt).all()
        # Flask-Smorest se postará o serializaci pomocí AuthorSchema(many=True)
        return authors

    @author_bp.arguments(AuthorCreateSchema)
    # Dekorátor definuje očekávaná vstupní data v těle požadavku.
    # - AuthorCreateSchema: Určuje Marshmallow schéma pro validaci vstupních dat.
    # - Pokud validace selže, automaticky vrátí chybu 422 Unprocessable Entity.
    # - Validovaná data jsou předána jako argument metody (zde 'new_author_data').
    @author_bp.response(201, AuthorSchema)
    # Dekorátor definuje úspěšnou odpověď pro vytvoření (HTTP 201 Created).
    # - AuthorSchema: Určuje, že odpověď bude jeden objekt serializovaný pomocí AuthorSchema.
    def post(self, new_author_data):
        """
        Vytvořit nového autora.
        Očekává data podle AuthorCreateSchema v těle POST požadavku.
        """
        # Vytvoření instance modelu Author z validovaných dat.
        # Předpokládá se, že AuthorCreateSchema neobsahuje pole, která by neměla být přímo přiřazena,
        # nebo že model Author má logiku pro zpracování těchto dat.
        author = Author(**new_author_data)

        try:
            # Přidání nového autora do databázové session.
            db.session.add(author)
            # Uložení změn do databáze.
            db.session.commit()
        except IntegrityError as e:
            # Odchytávání specifické chyby pro porušení unikátnosti (např. unikátní email nebo kombinace jmen).
            db.session.rollback()  # Vrácení transakce zpět
            # Logování chyby by bylo vhodné
            # print(f"IntegrityError: {e}")
            abort(
                409,  # Conflict
                message="Chyba při ukládání: Autor s těmito údaji již pravděpodobně existuje.",
            )
        except Exception as e:
            # Odchytávání obecné chyby pro jiné problémy při práci s databází.
            db.session.rollback()  # Vrácení transakce zpět
            # Logování chyby
            # print(f"Exception: {e}")
            abort(500, message="Interní chyba serveru při ukládání autora.")

        # Vrácení nově vytvořeného autora (serializace proběhne automaticky).
        return author

# Dekorátor registruje třídu pro danou cestu s parametrem na blueprintu


@author_bp.route("/<int:author_id>")
class AuthorResource(MethodView):
    """
    Resource pro operace s konkrétním autorem (/authors/<id>).
    Zpracovává GET (detail), PUT (aktualizace), DELETE (smazání).
    """

    @author_bp.response(200, AuthorSchema)
    # Odpověď pro úspěšné nalezení (HTTP 200 OK), serializovaná AuthorSchema.
    def get(self, author_id):
        """Získat detail autora podle ID."""
        # Načtení autora podle primárního klíče (author_id).
        # Moderní způsob získání podle PK
        author = db.session.get(Author, author_id)
        if author is None:
            # Pokud autor s daným ID nebyl nalezen, vrátí chybu 404 Not Found.
            abort(404, message="Autor nebyl nalezen.")
        # Flask-Smorest se postará o serializaci pomocí AuthorSchema.
        return author

    # Zde by mohlo být AuthorUpdateSchema, pokud se liší
    @author_bp.arguments(AuthorCreateSchema)
    # Dekorátor definuje očekávaná vstupní data v těle požadavku pro aktualizaci.
    # - AuthorCreateSchema (nebo lépe AuthorUpdateSchema): Určuje Marshmallow schéma pro validaci.
    @author_bp.response(200, AuthorSchema)
    # Dekorátor definuje úspěšnou odpověď pro aktualizaci (HTTP 200 OK).
    def put(self, update_data, author_id):
        """
        Aktualizovat existujícího autora.
        Očekává data podle AuthorCreateSchema (nebo lépe AuthorUpdateSchema) v těle PUT požadavku.
        """
        # Načtení existujícího autora z databáze.
        author = db.session.get(Author, author_id)
        if author is None:
            # Pokud autor neexistuje, vrátí chybu 404 Not Found.
            abort(404, message="Autor nebyl nalezen.")

        # Aktualizace atributů autora na základě poskytnutých dat.
        # Prochází všechny klíče a hodnoty v `update_data`.
        for key, value in update_data.items():
            # Nastaví atribut `key` na objektu `author` na hodnotu `value`.
            setattr(author, key, value)
        # Poznámka: Zde by mohla být přidána kontrola unikátnosti, pokud se mění pole, která musí být unikátní,
        # podobně jako v POST metodě nebo v PUT metodě pro Publishers.

        try:
            # Uložení změn do databáze.
            db.session.commit()
        except Exception as e:
            # Odchytávání obecné chyby při ukládání do databáze.
            db.session.rollback()
            # Logování chyby
            # print(f"Exception: {e}")
            abort(500, message="Interní chyba serveru při aktualizaci autora.")

        # Vrácení aktualizovaného autora (serializace proběhne automaticky).
        return author

    @author_bp.response(204)
    # Dekorátor definuje úspěšnou odpověď pro smazání (HTTP 204 No Content).
    def delete(self, author_id):
        """Smazat autora podle ID."""
        # Načtení autora, který má být smazán.
        author = db.session.get(Author, author_id)
        if author is None:
            # Pokud autor neexistuje, vrátí chybu 404 Not Found.
            abort(404, message="Autor nebyl nalezen.")

        try:
            # Smazání autora z databázové session.
            db.session.delete(author)
            # Potvrzení smazání v databázi.
            db.session.commit()
        except Exception as e:
            # Odchytávání obecné chyby při mazání z databáze.
            db.session.rollback()
            # Logování chyby
            # print(f"Exception: {e}")
            abort(500, message="Interní chyba serveru při mazání autora.")

        # Při úspěšném smazání se vrací prázdná odpověď s kódem 204 (nastaveno dekorátorem).
        return ""
