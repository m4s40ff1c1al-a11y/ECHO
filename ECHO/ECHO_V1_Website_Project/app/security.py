import os, hmac, hashlib, secrets, time
from cryptography.fernet import Fernet, InvalidToken

def hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return salt.hex() + "$" + digest.hex()

def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        test = hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return hmac.compare_digest(test, digest_hex)
    except Exception:
        return False

def get_cipher():
    key = os.getenv("DATA_ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("DATA_ENCRYPTION_KEY is not configured.")
    try:
        return Fernet(key.encode())
    except Exception as exc:
        raise RuntimeError("DATA_ENCRYPTION_KEY must be a valid Fernet key.") from exc

def encrypt_text(value: str) -> str:
    return get_cipher().encrypt(value.encode()).decode()

def decrypt_text(value: str) -> str:
    try:
        return get_cipher().decrypt(value.encode()).decode()
    except InvalidToken as exc:
        raise RuntimeError("Encrypted memory could not be decrypted. Check the encryption key.") from exc
