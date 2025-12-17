import os
import requests

# -------------------------------------------------
# CyborgDB Service URL
# (Docker internal DNS or local override)
# -------------------------------------------------
CYBORGDB_URL = os.getenv("CYBORGDB_URL", "http://cyborgdb:7700")


def insert_vector(hospital: str, case_id: str, enc_blob: dict):
    """
    Insert an encrypted vector into CyborgDB.

    CyborgDB INSERT EXPECTS (STRICT):
    {
        index: str,     # hospital name (federation boundary)
        id: str,        # case identifier
        vector: str,    # encrypted vector (ciphertext)
        nonce: str      # AES-GCM nonce
    }

    SECURITY GUARANTEES:
    - Ciphertext is NEVER decrypted
    - CyborgDB sees encrypted data only
    - Index enforces multi-hospital isolation
    """

    payload = {
        "index": hospital,
        "id": case_id,
        "vector": enc_blob["ciphertext"],  # ciphertext as opaque vector
        "nonce": enc_blob["nonce"],
    }

    response = requests.post(
        f"{CYBORGDB_URL}/insert",
        json=payload,
        timeout=5,
    )

    response.raise_for_status()
    return response.json()


def search_vectors(hospital: str, enc_query: dict, top_k: int = 5):
    """
    Search encrypted vectors in CyborgDB.

    CyborgDB SEARCH EXPECTS (STRICT):
    {
        index: str,     # hospital name
        vector: str,    # encrypted query vector (ciphertext)
        nonce: str,     # AES-GCM nonce
        top_k: int
    }

    ENCRYPTION-IN → ENCRYPTION-OUT
    - No plaintext ever exposed
    - Results are ciphertext references only
    """

    payload = {
        "index": hospital,
        "vector": enc_query["ciphertext"],
        "nonce": enc_query["nonce"],
        "top_k": top_k,
    }

    response = requests.post(
        f"{CYBORGDB_URL}/search",
        json=payload,
        timeout=5,
    )

    response.raise_for_status()
    return response.json()