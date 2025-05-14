from marshmallow import Schema  # Základní třída pro schémata z knihovny Marshmallow
# Plugin pro integraci Marshmallow schémat s APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask  # Základní třída pro Flask aplikaci
from flask_smorest import Api  # Rozšíření Flask-Smorest pro tvorbu REST API
from .config import config_by_name  # Import konfigurace definované v config.py
# Import instance databáze (db) a migračního nástroje (migrate) z db.py
from .db import db, migrate
import os  # Modul pro práci s operačním systémem, např. pro přístup k proměnným prostředí

# Vytvoření instance Flask-Smorest Api.
# Tuto instanci budeme používat pro registraci blueprintů a generování OpenAPI dokumentace.
smorest_api = Api()


schema_list = []


def custom_schema_name_resolver(schema_cls):
    """
    Vlastní resolver pro názvy schémat v OpenAPI dokumentaci.
    - Pro interní schémata Flask-Smorest (např. pro paginaci, chyby) používá jejich třídní název.
    - Pro uživatelská schémata preferuje hodnotu 'title' z vnořené třídy Meta.
    - Pokud 'Meta.title' není definováno, použije třídní název uživatelského schématu.
    """
    if hasattr(schema_cls, 'only') and getattr(schema_cls, 'only') is not None:
        return False

    # Kontrola, zda schéma pochází z balíčku flask_smorest
    if schema_cls.__module__.startswith("flask_smorest."):
        # Použije název třídy pro interní schémata Smorest
        schema_list.append([schema_cls.__name__, 1])
        return schema_cls.__name__

    # Pro uživatelská schémata
    if hasattr(schema_cls, 'Meta') and hasattr(schema_cls.Meta, 'title'):
        meta_title = getattr(schema_cls.Meta, 'title', None)
        if meta_title:  # Ujistíme se, že title není None nebo prázdný řetězec
            schema_list.append([meta_title, 2])
            return meta_title
    schema_list.append([schema_cls.__class__.__name__, 3])
    return schema_cls.__class__.__name__  # Fallback na název třídy


def create_app(config_name=None, config_override=None):
    """
    Factory funkce pro vytvoření a konfiguraci Flask aplikace.

    Tento vzor (Application Factory) umožňuje vytvářet více instancí aplikace
    s různými konfiguracemi, což je užitečné například pro vývoj, testování a produkci.

    Args:
        config_name (str, optional): Název konfigurace, která se má použít (např. 'development', 'production').
                                     Pokud není zadán, použije se hodnota z proměnné prostředí FLASK_CONFIG
                                     nebo 'default'.
        config_override (object, optional): Objekt s konfigurací, který přepíše hodnoty načtené
                                            z `config_by_name`. Používá se primárně pro testování.

    Returns:
        Flask: Nakonfigurovaná instance Flask aplikace.
    """
    # Pokud není název konfigurace explicitně zadán, pokusí se ho načíst
    # z proměnné prostředí 'FLASK_CONFIG'. Pokud ani ta není nastavena, použije se 'default'.
    if config_name is None:
        config_name = os.getenv("FLASK_CONFIG", "default")

    # Vytvoření základní instance Flask aplikace.
    # '__name__' je speciální proměnná v Pythonu, která zde odkazuje na název aktuálního modulu.
    # Flask ji používá k určení kořenové cesty aplikace pro hledání šablon a statických souborů.
    app = Flask(__name__)

    # Načtení konfigurace pro aplikaci.
    # Pokud je poskytnut `config_override`, použije se ten.
    # Jinak se konfigurace načte z objektu `config_by_name` na základě `config_name`.
    if config_override:
        app.config.from_object(config_override)
    else:
        app.config.from_object(config_by_name[config_name])

    # Inicializace rozšíření Flask s vytvořenou aplikací.
    # Metoda `init_app` umožňuje inicializovat rozšíření až poté, co je instance aplikace vytvořena.
    # To je důležité pro vzor Application Factory.

    # Inicializace SQLAlchemy (databázového ORM)
    db.init_app(app)
    # Inicializace Flask-Migrate (nástroje pro správu databázových migrací)
    migrate.init_app(app, db)

    # Inicializace Flask-Smorest.
    # Flask-Smorest se stará o generování OpenAPI dokumentace, validaci požadavků
    # a serializaci odpovědí pomocí Marshmallow schémat.
    # `spec_kwargs` umožňuje předat další argumenty konstruktoru APISpec.
    # `MarshmallowPlugin` zajišťuje integraci s Marshmallow.
    # Použití vlastního resolveru pro názvy schémat.
    ma_plugin = MarshmallowPlugin(
        schema_name_resolver=custom_schema_name_resolver)
    smorest_api.init_app(app, spec_kwargs=dict(marshmallow_plugin=ma_plugin))

    # Registrace Blueprintů.
    # Blueprints umožňují modulárně organizovat routy a pohledy v aplikaci.
    # Zde importujeme blueprint `api_v1_bp` z modulu `app.api`.
    from .api import api_v1_bp  # Import blueprintu pro API verze 1

    # Registrace blueprintu `api_v1_bp` u instance Flask-Smorest `smorest_api`.
    # Všechny routy definované v tomto blueprintu budou dostupné pod prefixem
    # definovaným při vytváření blueprintu (např. /api/v1).
    smorest_api.register_blueprint(api_v1_bp)

    # Zde můžete přidat další blueprinty, pokud by vaše aplikace měla například
    # i webové rozhraní oddělené od REST API.
    # from .web import web_bp  # Příklad
    # app.register_blueprint(web_bp) # Běžné Flask Blueprints se registrují přímo na 'app'

    # Definice kontextu pro Flask shell.
    # `flask shell` je interaktivní Python konzole, která má již načtenou
    # vaši aplikaci a její kontext. Toto usnadňuje ladění a testování.
    # Funkce označená `@app.shell_context_processor` vrací slovník,
    # jehož klíče budou automaticky dostupné jako proměnné v `flask shell`.
    @app.shell_context_processor
    def make_shell_context():
        # Zpřístupníme instanci databáze (db) a například model User.
        # Můžete sem přidat další modely nebo objekty, které chcete mít k dispozici.
        from .models import User  # Příklad importu modelu
        return {"db": db, "User": User}

    # Jednoduchá testovací routa na kořenovém URL aplikace.
    # Slouží pro rychlé ověření, že aplikace běží.
    @app.route("/hello")
    def hello():
        return "Hello, World from Flask IS Template!"

    # Vrácení nakonfigurované instance aplikace.
    return app
