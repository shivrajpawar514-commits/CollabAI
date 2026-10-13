import os
import hmac
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Dict
import jwt

from app.core.config import settings

# Salted PBKDF2-HMAC-SHA256 password hashing (100,000 iterations)
# Pure standard library - robust, zero external C-dependency build failures
ITERATIONS = 100_000


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"pbkdf2:sha256:{ITERATIONS}${base64.b64encode(salt).decode('ascii')}${base64.b64encode(pw_hash).decode('ascii')}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        parts = hashed_password.split("$")
        if len(parts) != 3:
            return False
        meta, salt_b64, hash_b64 = parts
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected_hash = base64.b64decode(hash_b64.encode("ascii"))
        algo_parts = meta.split(":")
        iterations = int(algo_parts[2]) if len(algo_parts) > 2 else ITERATIONS
        calc_hash = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(calc_hash, expected_hash)
    except Exception:
        return False


def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "access"
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(subject),
        "iat": now,
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
