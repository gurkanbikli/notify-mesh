import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt
from cryptography.fernet import Fernet

from app.core.config import settings
from app.models.admin_user import AdminUserRole


def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + ":" + key.hex()


def verify_password(plain: str, hashed: str) -> bool:
    salt_hex, key_hex = hashed.split(":")
    key = hashlib.pbkdf2_hmac("sha256", plain.encode(), bytes.fromhex(salt_hex), 100_000)
    return key.hex() == key_hex


def create_access_token(subject: str, role: AdminUserRole) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire, "iat": now, "jti": str(uuid4())}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def generate_temp_password() -> str:
    return secrets.token_urlsafe(12)


def generate_api_key() -> tuple[str, str, str]:
    """Returns (raw_key, key_prefix, key_hash). Store prefix and hash; return raw once."""
    raw = "nm_" + secrets.token_urlsafe(32)
    prefix = raw[:8]
    key_hash = bcrypt.hashpw(raw.encode(), bcrypt.gensalt()).decode()
    return raw, prefix, key_hash


def verify_api_key(raw: str, key_hash: str) -> bool:
    return bcrypt.checkpw(raw.encode(), key_hash.encode())


def _fernet() -> Fernet:
    return Fernet(settings.channel_encryption_key.encode())


def encrypt_config(config: dict) -> str:
    return _fernet().encrypt(json.dumps(config).encode()).decode()


def decrypt_config(token: str) -> dict:
    return json.loads(_fernet().decrypt(token.encode()))
