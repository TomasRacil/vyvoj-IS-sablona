from .db import db
from sqlalchemy.sql import func
import datetime


# Příklad modelu - upravte dle potřeb vašeho IS
class User(db.Model):
    __tablename__ = "users"  # Dobrá praxe explicitně pojmenovat tabulku

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    # Heslo by mělo být hashované - použijte např. Werkzeug security helpers
    # password_hash = db.Column(db.String(128))

    def __repr__(self):
        return f"<User {self.username}>"


# Přidejte další modely podle vaší aplikace (např. Závody, Registrace, Výsledky...)
# class Event(db.Model):
#     __tablename__ = 'events'
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(100), nullable=False)
#     date = db.Column(db.Date, nullable=False)
