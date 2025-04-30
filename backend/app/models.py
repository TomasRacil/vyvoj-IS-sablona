# Tento soubor definuje databázové modely pomocí SQLAlchemy ORM.
# Každá třída zde reprezentuje jednu tabulku v databázi.

from .db import db  # Import instance SQLAlchemy z db.py
from sqlalchemy.sql import func  # Import SQL funkcí (např. pro server_default)
# Import modulu datetime (i když není přímo použitý, může se hodit)
import datetime
# from werkzeug.security import generate_password_hash, check_password_hash # Příklad pro hashování hesel

# Model pro uživatele (User)


class User(db.Model):
    """
    Model reprezentující uživatele v informačním systému.
    """
    # Explicitní pojmenování tabulky v databázi - dobrá praxe
    __tablename__ = "users"

    # Primární klíč - unikátní identifikátor záznamu
    id = db.Column(db.Integer, primary_key=True)

    # Sloupec pro uživatelské jméno (řetězec, max 80 znaků, unikátní, povinný)
    username = db.Column(db.String(80), unique=True, nullable=False)

    # Sloupec pro email (řetězec, max 120 znaků, unikátní, povinný)
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Sloupec pro datum a čas vytvoření záznamu s časovou zónou
    # server_default=func.now() zajistí automatické nastavení času databázovým serverem
    # při vytvoření záznamu. To je obecně preferovanější než `default=datetime.utcnow`.
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    # Sloupec pro hashované heslo (řetězec, délka závisí na hashovacím algoritmu)
    # Je KRITICKY DŮLEŽITÉ ukládat pouze hash hesla, nikdy ne čisté heslo!
    # password_hash = db.Column(db.String(128), nullable=False) # Heslo by mělo být povinné

    # Metody pro práci s heslem (příklad s Werkzeug)
    # def set_password(self, password):
    #     """Generuje hash hesla a uloží ho."""
    #     self.password_hash = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     """Kontroluje, zda zadané heslo odpovídá uloženému hashi."""
    #     return check_password_hash(self.password_hash, password)

    # Metoda pro reprezentaci objektu jako řetězce (užitečné pro ladění)
    def __repr__(self):
        return f"<User {self.username}>"


# Zde můžete přidat další modely podle potřeb vaší aplikace
# Například pro závody (Events), registrace (Registrations), výsledky (Results), atd.

# class Event(db.Model):
#     """Model reprezentující závod nebo událost."""
#     __tablename__ = 'events' # Explicitní název tabulky
#
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False) # Název události
#     date = db.Column(db.Date, nullable=False) # Datum konání
#     description = db.Column(db.Text) # Delší popis události
#     created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
#
#     # Příklad relace (pokud by existoval model Registration)
#     # registrations = db.relationship('Registration', backref='event', lazy=True)
#
#     def __repr__(self):
#         return f"<Event {self.name} ({self.date})>"

# class Registration(db.Model):
#     """Model reprezentující registraci uživatele na závod."""
#     __tablename__ = 'registrations'
#
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Cizí klíč na tabulku users
#     event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=False) # Cizí klíč na tabulku events
#     registration_time = db.Column(db.DateTime(timezone=True), server_default=func.now())
#     status = db.Column(db.String(50)) # Např. 'confirmed', 'pending', 'cancelled'
#
#     # Relace pro snadný přístup k propojeným objektům
#     user = db.relationship('User', backref=db.backref('registrations', lazy=True))
#     # backref pro Event je definován v modelu Event
#
#     # Unikátní omezení, aby se uživatel nemohl registrovat vícekrát na stejný závod
#     __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='uq_user_event_registration'),)
#
#     def __repr__(self):
#         return f"<Registration user={self.user_id} event={self.event_id}>"
