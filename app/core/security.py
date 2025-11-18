from datetime import datetime, timedelta, timezone
import jwt
import bcrypt

from core.config import settings


def hash_password(raw: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(raw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(raw: str, hashed: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(raw.encode('utf-8'), hashed.encode('utf-8'))


def _make_token(sub: str, minutes: int) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {"sub": sub, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=minutes)).timestamp())}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def create_access_token(sub: str) -> str:
    return _make_token(sub, settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(sub: str, days: int | None = None) -> str:
    mins = (days or settings.REFRESH_TOKEN_EXPIRE_DAYS) * 24 * 60
    return _make_token(sub, mins)
