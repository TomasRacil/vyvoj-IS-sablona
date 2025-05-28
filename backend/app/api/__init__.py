from flask_smorest import Blueprint
from app.api.routes import *


# Vytvoření Blueprintu pro API verze 1
# První argument: název blueprintu
# Druhý argument: __name__ (pro hledání zdrojů)
# url_prefix: prefix pro všechny routy v tomto blueprintu
# description: popis pro OpenAPI dokumentaci
api_v1_bp = Blueprint(
    "api_v1", __name__, url_prefix="/api/v1", description="API Verze 1 pro IS Šablonu"
)
# Registrace dílčích blueprintů
api_v1_bp.register_blueprint(auth_bp)
api_v1_bp.register_blueprint(author_bp)
api_v1_bp.register_blueprint(book_bp)
api_v1_bp.register_blueprint(publisher_bp)
api_v1_bp.register_blueprint(user_bp)
