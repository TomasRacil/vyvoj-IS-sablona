# Základní třída pro pohledy založené na třídách
from flask.views import MethodView
# Funkce pro generování HTTP chybových odpovědí
from flask_smorest import abort

# Importy z vaší aplikace
from app.models import Publisher  # Import databázového modelu Publisher
# Import Marshmallow schémat
from app.schemas import PublisherSchema, PublisherCreateSchema, PublisherUpdateSchema
from app.db import db  # Import instance SQLAlchemy databáze
# Výjimka pro odchytávání chyb databázové integrity
from sqlalchemy.exc import IntegrityError  # Pro odchytávání chyb unikátnosti
# Import blueprintu
from app.api import api_v1_bp

# --- Endpointy pro vydavatele ---

# Registrace třídy PublishersResource pro URL cestu "/publishers"


@api_v1_bp.route("/publishers")
class PublishersResource(MethodView):
    """
    Resource pro operace s kolekcí vydavatelů.
    Resource pro operace s kolekcí vydavatelů (/publishers).
    Zpracovává GET (seznam) a POST (vytvoření).
    """

    # Dekorátor pro GET: odpověď bude HTTP 200 s polem objektů serializovaných PublisherSchema.
    @api_v1_bp.response(200, PublisherSchema(many=True))
    def get(self):
        """Získat seznam všech vydavatelů."""
        # Vytvoření dotazu pro výběr všech vydavatelů, seřazených podle jména.
        stmt = db.select(Publisher).order_by(Publisher.name)
        # Provedení dotazu a načtení všech výsledků.
        publishers = db.session.scalars(stmt).all()
        # Vrácení seznamu vydavatelů (Flask-Smorest zajistí serializaci).
        return publishers

    # Dekorátor pro POST: očekává data validovaná PublisherCreateSchema.
    @api_v1_bp.arguments(PublisherCreateSchema)
    # Dekorátor pro POST: úspěšná odpověď bude HTTP 201 s jedním objektem serializovaným PublisherSchema.
    @api_v1_bp.response(201, PublisherSchema)
    def post(self, new_publisher_data):
        """
        Vytvořit nového vydavatele.
        Očekává data podle PublisherCreateSchema v těle POST požadavku.
        """
        if db.session.scalars(db.select(Publisher).where(
            # Kontrola, zda již neexistuje vydavatel se stejným jménem.
            (Publisher.name == new_publisher_data["name"])
        )).first():
            # Pokud ano, vrátí HTTP 409 Conflict.
            abort(
                409, message="Vydavatel s tímto jménem již existuje."
            )

        # Vytvoření nové instance modelu Publisher z validovaných dat.
        publisher = Publisher(**new_publisher_data)

        try:
            # Přidání nového vydavatele do databázové session.
            db.session.add(publisher)
            # Uložení změn do databáze.
            db.session.commit()
        except IntegrityError as e:
            # V případě chyby integrity (např. duplicitní jméno, pokud je unikátní).
            db.session.rollback()
            abort(
                409,
                message="Chyba při ukládání: Vydavatel s tímto jménem již pravděpodobně existuje.",
            )
        except Exception as e:
            # V případě jakékoliv jiné chyby.
            db.session.rollback()
            # print(f"Exception: {e}")
            abort(
                500, message=f"Interní chyba serveru při ukládání vydavatele: {str(e)}")

        # Vrácení nově vytvořeného vydavatele (Flask-Smorest zajistí serializaci).
        return publisher

# Registrace třídy PublisherResource pro URL cestu "/publishers/<int:publisher_id>"
# @api_v1_bp.route("/publishers/<int:publisher_id>") # Chyba v původním kódu, mělo by být zde
# Opraveno: Přesunuto na správné místo před definici třídy


@api_v1_bp.route("/publishers/<int:publisher_id>")
class PublisherResource(MethodView):
    """
    Resource pro operace s konkrétním vydavatelem, identifikovaným pomocí ID.
    Resource pro operace s konkrétním vydavatelem (/publisher/<id>).
    Zpracovává GET (detail), PUT (aktualizace), DELETE (smazání).
    """
    # Dekorátor pro GET: odpověď bude HTTP 200 s jedním objektem serializovaným PublisherSchema.
    @api_v1_bp.response(200, PublisherSchema)
    def get(self, publisher_id):
        """Získat detail vydavatele podle ID."""
        # Načtení vydavatele podle primárního klíče.
        publisher = db.session.get(Publisher, publisher_id)
        if publisher is None:
            # Pokud vydavatel neexistuje, vrátí HTTP 404 Not Found.
            abort(404, message="Vydavatel nebyl nalezen.")
        return publisher

    # Dekorátor pro PUT: očekává data validovaná PublisherUpdateSchema.
    @api_v1_bp.arguments(PublisherUpdateSchema)
    # Dekorátor pro PUT: úspěšná odpověď bude HTTP 200 s jedním objektem serializovaným PublisherSchema.
    @api_v1_bp.response(200, PublisherSchema)
    def put(self, update_data, publisher_id):
        """
        Aktualizovat existujícího vydavatele (celý záznam).
        Očekává data podle PublisherUpdateSchema v těle PUT požadavku.
        """
        publisher = db.session.get(Publisher, publisher_id)
        if publisher is None:
            abort(404, message="Vydavatel nebyl nalezen.")

        # Volitelná kontrola: Pokud se aktualizuje jméno, zkontrolujte,
        # zda nové jméno již nepoužívá jiný vydavatel.
        new_name = update_data.get("name")
        if new_name and new_name != publisher.name:
            # Hledání jiného vydavatele (s jiným ID) se stejným novým jménem.
            if db.session.scalars(db.select(Publisher).where(
                Publisher.name == new_name,
                Publisher.publisher_id != publisher_id
            )).first():
                abort(
                    409,
                    message=f"Vydavatel s názvem '{new_name}' již existuje."
                )

        # Aktualizace atributů vydavatele na základě poskytnutých dat.
        # PublisherUpdateSchema by měla definovat, která pole lze aktualizovat.
        for key, value in update_data.items():
            setattr(publisher, key, value)

        # Uložení změn do databáze.
        db.session.commit()
        # Vrácení aktualizovaného vydavatele.
        return publisher

    # Dekorátor pro DELETE: úspěšná odpověď bude HTTP 204 No Content.
    @api_v1_bp.response(204)
    def delete(self, publisher_id):
        """Smazat vydavatele podle ID."""
        # Načtení vydavatele podle ID.
        publisher = db.session.get(Publisher, publisher_id)
        if publisher is None:
            abort(404, message="Vydavatel nebyl nalezen.")

        # Smazání vydavatele z databázové session.
        db.session.delete(publisher)
        # Uložení změn (provedení DELETE příkazu).
        db.session.commit()
        # Vrácení prázdné odpovědi (status 204 je nastaven dekorátorem).
        return ""
