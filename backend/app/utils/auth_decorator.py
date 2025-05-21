from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from flask_smorest import abort

from app.models import User, TokenBlacklist  # Přidán import TokenBlacklist
from app.utils.enums import UserRoleEnum  # Import enumerace rolí
from enum import Enum  # Pro kontrolu instance Enum
from app import db  # Import db pro dotazy


def access_control(required_roles=None, allow_owner=False, owner_id_param_name=None):
    """
    Dekorátor pro ochranu endpointů na základě uživatelských rolí a/nebo vlastnictví.
    Vyžaduje, aby byl uživatel autentizován pomocí JWT.
    Role se získávají z databáze. Vlastnictví se ověřuje porovnáním ID uživatele
    z JWT s ID získaným z URL parametru.

    :param required_roles: Seznam, n-tice, jeden název role (string nebo UserRoleEnum),
                           nebo None. Role, které mají přístup.
    :param allow_owner: bool, Pokud True, povolí přístup vlastníkovi zdroje.
    :param owner_id_param_name: string, Název URL parametru, který obsahuje ID vlastníka zdroje
                                (např. 'user_id' pro endpoint /users/<int:user_id>).
                                Tento parametr je nutný, pokud allow_owner=True.
    """
    processed_required_roles = []
    if required_roles:
        if not isinstance(required_roles, (list, tuple)):
            required_roles_list = [required_roles]
        else:
            required_roles_list = list(required_roles)

        for role in required_roles_list:
            if isinstance(role, UserRoleEnum):
                processed_required_roles.append(role.value)
            elif isinstance(role, str):
                processed_required_roles.append(role)
            else:
                raise ValueError(
                    "Role v required_roles musí být string nebo UserRoleEnum.")

    if allow_owner and not owner_id_param_name:
        raise ValueError(
            "owner_id_param_name musí být specifikován, pokud allow_owner=True.")

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()  # Ověří, že platný JWT je přítomen a neprošlý

            # Kontrola, zda je token na blacklistu
            jti = get_jwt()["jti"]
            token_is_blacklisted = db.session.execute(
                db.select(TokenBlacklist).filter_by(jti=jti)
            ).scalar_one_or_none()

            if token_is_blacklisted:
                abort(401, message="Token byl odvolán (je na blacklistu).")

            current_user_id_from_jwt = get_jwt_identity()  # Získá identitu uživatele z JWT

            # Použití db.session.get pro načtení podle PK
            user = db.session.get(User, current_user_id_from_jwt)
            if not user:
                abort(401, message="Uživatel asociovaný s tokenem nenalezen.")

            access_granted = False

            # 1. Kontrola vlastnictví
            if allow_owner:  # owner_id_param_name je již validován
                target_owner_id_from_request = kwargs.get(owner_id_param_name)
                if target_owner_id_from_request is not None:
                    # Předpokládáme, že current_user_id_from_jwt (z tokenu) a
                    # target_owner_id_from_request (z URL parametru, např. <int:user_id>)
                    # jsou stejného typu (např. int) pro přímé porovnání.
                    if current_user_id_from_jwt == target_owner_id_from_request:
                        access_granted = True

            # 2. Kontrola rolí (pokud přístup ještě nebyl udělen vlastnictvím)
            if not access_granted and processed_required_roles:
                user_role_names = {role.name for role in user.roles.all()}

                if not user_role_names:  # Uživatel nemá žádné role
                    # Tato zpráva se zobrazí, pouze pokud jsou role vyžadovány (processed_required_roles není prázdný)
                    # a uživatel není vlastník (nebo vlastnictví není povoleno/kontrolováno).
                    abort(403, message="Uživatel nemá přiřazené žádné role.")

                if any(req_role in user_role_names for req_role in processed_required_roles):
                    access_granted = True

            if access_granted:
                return fn(*args, **kwargs)
            else:
                error_parts = []
                if processed_required_roles:
                    roles_str = ", ".join(processed_required_roles)
                    error_parts.append(f"jedna z rolí: {roles_str}")
                if allow_owner and owner_id_param_name:  # Přidáme info o vlastnictví pouze pokud bylo relevantní
                    error_parts.append("vlastnictví zdroje")

                if error_parts:
                    message = f"Přístup odepřen. Vyžadováno: {' nebo '.join(error_parts)}."
                else:
                    # Tento případ nastane, pokud dekorátor byl použit bez specifikace rolí
                    # a bez povolení kontroly vlastnictví, nebo pokud obě kontroly selhaly.
                    message = "Přístup odepřen. Nejsou splněny podmínky pro přístup."
                abort(403, message=message)
        return wrapper
    return decorator
