import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

JWT_ALGORITHM = "HS256"
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_int_env(name: str, default: str) -> int:
    value = os.getenv(name, default)
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid int for {name}") from exc


def get_jwt_settings() -> dict:
    access_secret = os.getenv("JWT_ACCESS_SECRET")
    refresh_secret = os.getenv("JWT_REFRESH_SECRET")
    if not access_secret or not refresh_secret:
        raise RuntimeError("JWT_ACCESS_SECRET/JWT_REFRESH_SECRET must be set")
    return {
        "access_secret": access_secret,
        "refresh_secret": refresh_secret,
        "access_ttl": _get_int_env("JWT_ACCESS_TTL_SECONDS", "900"),
        "refresh_ttl": _get_int_env("JWT_REFRESH_TTL_SECONDS", "2592000"),
    }


def hash_password(password: str) -> str:
    pepper = os.getenv("PASSWORD_HASH_PEPPER", "")
    return PWD_CONTEXT.hash(f"{password}{pepper}")


def verify_password(password: str, password_hash: str) -> bool:
    pepper = os.getenv("PASSWORD_HASH_PEPPER", "")
    return PWD_CONTEXT.verify(f"{password}{pepper}", password_hash)


def create_access_token(user_id: str, tenant_id: str, role: str) -> str:
    settings = get_jwt_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings["access_ttl"])).timestamp()),
    }
    return jwt.encode(payload, settings["access_secret"], algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str, tenant_id: str, role: str) -> str:
    settings = get_jwt_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "tid": str(tenant_id),
        "role": role,
        "typ": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=settings["refresh_ttl"])).timestamp()),
    }
    return jwt.encode(payload, settings["refresh_secret"], algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    settings = get_jwt_settings()
    return jwt.decode(token, settings["access_secret"], algorithms=[JWT_ALGORITHM])


def decode_refresh_token(token: str) -> dict:
    settings = get_jwt_settings()
    payload = jwt.decode(token, settings["refresh_secret"], algorithms=[JWT_ALGORITHM])
    if payload.get("typ") != "refresh":
        raise jwt.InvalidTokenError("Invalid refresh token")
    return payload


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
