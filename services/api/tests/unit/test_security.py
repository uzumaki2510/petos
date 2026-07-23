from petos_api.core.security import (
    hash_password,
    verify_password,
    generate_session_token,
    hash_session_token,
    verify_bff_secret,
)


def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    assert hashed.startswith("$argon2id$")

    is_valid, new_hash = verify_password(password, hashed)
    assert is_valid is True
    assert new_hash is None


def test_password_verification_fails():
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)

    is_valid, new_hash = verify_password("wrong_password", hashed)
    assert is_valid is False
    assert new_hash is None


def test_session_token():
    token = generate_session_token()
    assert len(token) > 20

    hashed = hash_session_token(token)
    assert len(hashed) == 64  # SHA-256 hex digest length


def test_verify_bff_secret():
    secret = "my_secret"
    assert verify_bff_secret(secret, secret) is True
    assert verify_bff_secret("wrong", secret) is False
    assert verify_bff_secret("", secret) is False
