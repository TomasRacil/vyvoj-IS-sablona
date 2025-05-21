from app import db
from sqlalchemy.sql import func
import datetime


class TokenBlacklist(db.Model):
    """
    Model pro ukládání JTI (JWT ID) blacklistovaných tokenů.
    """
    __tablename__ = "token_blacklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<TokenBlacklist jti={self.jti}>"
