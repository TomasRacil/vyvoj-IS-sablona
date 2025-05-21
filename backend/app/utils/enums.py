from enum import Enum


class UserRoleEnum(Enum):
    """
    Enumerace definující dostupné uživatelské role.
    Hodnoty odpovídají sloupci 'name' v tabulce 'roles'.
    """
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    USER = "user"

    # Přidejte další role podle potřeby
