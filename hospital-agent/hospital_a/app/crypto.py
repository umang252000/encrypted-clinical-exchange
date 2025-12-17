# hospital-agent/.../app/crypto.py

import os
import json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# KEY_MODE = "file" → load or auto-generate local key
# KEY_MODE = "kms"  → fetch key from KMS (kms_client.fetch_key)
KEY_MODE = os.getenv('KEY_MODE', 'file')  # 'file' or 'kms'


# -------------------------------------------------------------
# FILE MODE: load or auto-generate AES-256 key
# -------------------------------------------------------------

def load_key(path: str) -> bytes:
    """Load key from a local file."""
    with open(path, 'rb') as f:
        return f.read()


def generate_key(path: str) -> bytes:
    """Generate AES-256 key and store it securely."""
    key = AESGCM.generate_key(bit_length=256)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, 'wb') as f:
        f.write(key)

    # Secure file permissions (best effort)
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass

    return key


def load_key_auto(path: str, kms_fetcher=None) -> bytes:
    """
    Unified key loader:

    - FILE MODE → load or auto-generate AES-256 key
    - KMS  MODE → fetch key using kms_fetcher()

    """
    if KEY_MODE == 'file':
        if not os.path.exists(path):
            return generate_key(path)
        return load_key(path)

    elif KEY_MODE == 'kms':
        if kms_fetcher is None:
            raise RuntimeError("KMS fetcher required for KEY_MODE=kms")
        return kms_fetcher()

    else:
        raise RuntimeError(f"Unknown KEY_MODE '{KEY_MODE}'")


# -------------------------------------------------------------
# AES-GCM ENCRYPT / DECRYPT
# -------------------------------------------------------------

def encrypt_vector(key: bytes, plaintext_bytes: bytes) -> dict:
    """
    Encrypt raw bytes using AES-GCM with a random nonce.
    Suitable for embedding vectors.
    """
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext_bytes, None)

    return {
        "nonce": nonce.hex(),
        "ciphertext": ct.hex()
    }


def encrypt_blob(key: bytes, obj: dict) -> dict:
    """
    Encrypt a Python dict using AES-GCM.
    This is used for /ingest_example where we encrypt structured JSON.
    """
    # Convert payload → bytes
    plaintext = json.dumps(obj).encode("utf-8")

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, plaintext, None)

    return {
        "nonce": nonce.hex(),
        "ciphertext": ct.hex()
    }


def decrypt_vector(key: bytes, nonce_hex: str, ciphertext_hex: str) -> bytes:
    """
    Decrypt AES-GCM encrypted bytes.
    """
    aesgcm = AESGCM(key)
    nonce = bytes.fromhex(nonce_hex)
    ct = bytes.fromhex(ciphertext_hex)

    return aesgcm.decrypt(nonce, ct, None)