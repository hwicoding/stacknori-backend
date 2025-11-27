from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()


def _create_token(subject: str, minutes: int, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=minutes)
    payload = {
        "sub": subject,
        "exp": expires,
        "iat": now,
        "jti": uuid4().hex,
        "type": token_type,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    minutes = (
        int(expires_delta.total_seconds() / 60)
        if expires_delta
        else settings.access_token_expire_minutes
    )
    return _create_token(subject, minutes, token_type="access")


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject,
        settings.refresh_token_expire_minutes,
        token_type="refresh",
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


class InvalidTokenError(Exception):
    """Raised when JWT verification fails."""


def validate_token(token: str, expected_type: str = "access") -> dict[str, Any]:
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise InvalidTokenError(str(exc)) from exc

    token_type = payload.get("type")
    if expected_type and token_type != expected_type:
        raise InvalidTokenError(f"Invalid token type: {token_type}")
    return payload

