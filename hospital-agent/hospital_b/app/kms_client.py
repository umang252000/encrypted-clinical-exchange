# hospital-agent/hospital_b/app/kms_client.py
import os

"""
KMS Key Loader for Hospital Agent
---------------------------------
Supports:
 - FILE MODE   → load key from local mounted path
 - KMS MODE    → simulated KMS fetch (can later be replaced by AWS/GCP/Azure SDK)

Environment variables:
 - KEY_MODE        = "file" or "kms"
 - FILE_KEY_PATH   = path to local key file
 - KMS_KEY_PATH    = simulated KMS mount path
"""

def fetch_key():
    mode = os.getenv("KEY_MODE", "file").lower()

    if mode == "file":
        return _load_from_file()

    elif mode == "kms":
        return _load_from_kms()

    else:
        raise RuntimeError(f"Invalid KEY_MODE '{mode}', expected 'file' or 'kms'")


# ---------------------------------------------------------
# FILE MODE
# ---------------------------------------------------------
def _load_from_file():
    path = os.getenv("FILE_KEY_PATH", "/keys/hospital_b.key")

    if not os.path.exists(path):
        raise RuntimeError(f"[FILE MODE] Key not found at {path}")

    with open(path, "rb") as f:
        return f.read()


# ---------------------------------------------------------
# SIMULATED KMS MODE
# ---------------------------------------------------------
def _load_from_kms():
    """
    This simulates a cloud KMS by reading from a mounted secret path.
    Replace this logic later with AWS KMS / GCP KMS / Azure Key Vault.
    """
    path = os.getenv("KMS_KEY_PATH", "/keys_kms/hospital_b.key")

    if not os.path.exists(path):
        raise RuntimeError(f"[KMS MODE] KMS key not found at {path}")

    with open(path, "rb") as f:
        return f.read()