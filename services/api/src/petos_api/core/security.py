import secrets
import hashlib
from typing import Tuple, Optional
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

# 1. Final Argon2id configuration
# Algorithm: Argon2id
# Memory cost: 65536 KiB (64 MB)
# Time cost: 3
# Parallelism: 1
password_hash = PasswordHash(
    (
        Argon2Hasher(
            time_cost=3,
            memory_cost=65536,
            parallelism=1,
        ),
    )
)


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> Tuple[bool, Optional[str]]:
    """
    Returns (is_valid, new_hash)
    """
    return password_hash.verify_and_update(password, hashed_password)


def generate_session_token() -> str:
    """Generate a 256-bit random session token."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Hash the session token using SHA-256 for database storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def verify_bff_secret(secret: str, expected_secret: str) -> bool:
    """Constant-time validation of BFF secret."""
    if not secret or not expected_secret:
        return False
    return secrets.compare_digest(secret, expected_secret)
