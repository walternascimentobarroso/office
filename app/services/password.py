"""Password hashing and verification service."""

from __future__ import annotations

import hashlib
import hmac
import secrets

PBKDF2_ITERATIONS = 600_000
SALT_SIZE = 16
ALGORITHM = "sha256"


class PasswordService:
    """Generates and validates password hashes."""

    def hash_password(self, plain_password: str) -> str:
        """Hash password using PBKDF2-HMAC with random salt."""

        salt = secrets.token_hex(SALT_SIZE)
        digest = hashlib.pbkdf2_hmac(
            ALGORITHM,
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ITERATIONS,
        ).hex()
        return f"pbkdf2_{ALGORITHM}${PBKDF2_ITERATIONS}${salt}${digest}"

    def verify_password(self, plain_password: str, password_hash: str | None) -> bool:
        """Verify plaintext password against stored hash."""

        if not password_hash:
            return False
        try:
            scheme, iterations_str, salt, expected_digest = password_hash.split("$", 3)
            if scheme != f"pbkdf2_{ALGORITHM}":
                return False
            iterations = int(iterations_str)
        except (ValueError, TypeError):
            return False

        derived_digest = hashlib.pbkdf2_hmac(
            ALGORITHM,
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        ).hex()
        return hmac.compare_digest(derived_digest, expected_digest)
