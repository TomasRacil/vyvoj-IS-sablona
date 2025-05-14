# Tato složka definuje schémata pomocí knihovny Marshmallow.
# Schémata slouží k:
# 1. Serializaci: Převod komplexních objektů (např. SQLAlchemy modely) na jednoduché Python datové typy (slovníky, seznamy),
#    které lze snadno převést na JSON pro API odpovědi.
# 2. Deserializaci: Převod jednoduchých datových typů (např. z JSON těla požadavku) na Python objekty.
# 3. Validaci: Kontrola, zda data (přijatá v požadavku nebo před serializací) splňují definovaná pravidla
#    (např. typ, povinnost, délka, formát).
# Flask-Smorest tato schémata využívá pro automatickou validaci požadavků (@arguments)
# a formátování odpovědí (@response).