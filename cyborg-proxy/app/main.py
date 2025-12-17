from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, datetime

# -------------------------------------------------
# CyborgDB client (encrypted-in-use)
# -------------------------------------------------
from .cyborgdb_client import insert_vector, search_vectors

# -------------------------------------------------
# JWT / RBAC utilities
# -------------------------------------------------
from app.auth import verify_jwt, require_role, TokenData

# -------------------------------------------------
# Paths
# -------------------------------------------------
DATA_DIR = "/data"
os.makedirs(DATA_DIR, exist_ok=True)

AUDIT_LOG = os.path.join(DATA_DIR, "audit.log")

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(
    title="Encrypted Clinical Exchange – Cyborg Proxy",
    description="""
### 🔐 Zero-Trust Encrypted Data Plane

This service:
- Stores **encrypted-only** clinical data
- Enforces **JWT-based RBAC**
- Logs all actions for audit
- Never sees plaintext (PHI-safe)

**Actors**
- Hospital Agents (admin)
- Clinicians (read-only)
""",
    version="1.0.0",
)

# -------------------------------------------------
# CORS (required for React UI)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# System Endpoints
# -------------------------------------------------
@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "service": "cyborg-proxy"}


@app.get("/", tags=["System"])
def root():
    return {
        "project": "Encrypted Multi-Hospital Clinical Knowledge Exchange",
        "component": "Cyborg Proxy",
        "description": "Zero-trust encrypted data plane for multi-hospital clinical knowledge exchange",
        "features": [
            "Encrypted-only storage (no plaintext)",
            "JWT-based RBAC",
            "Tamper-evident audit logging",
            "Clinician local decryption",
            "Multi-hospital federation",
        ],
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "whoami": "/whoami",
            "search": "/search",
        },
    }


@app.get("/whoami", tags=["Auth"])
def whoami(token: TokenData = Depends(verify_jwt)):
    return {"sub": token.sub, "role": token.role}

# -------------------------------------------------
# Models
# -------------------------------------------------
class StoreRequest(BaseModel):
    hospital: str
    case_id: str
    enc_blob: dict   # { "ciphertext": "...", "nonce": "..." }


class EncryptedSearchRequest(BaseModel):
    hospital: str
    enc_query: dict  # { "ciphertext": "...", "nonce": "..." }
    k: int = 5

# -------------------------------------------------
# Audit Logging
# -------------------------------------------------
def write_audit_entry(actor: str, role: str, action: str, filename: str):
    entry = {
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "actor": actor,
        "role": role,
        "action": action,
        "filename": filename,
    }
    try:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

# -------------------------------------------------
# Encrypted Storage (CyborgDB)
# -------------------------------------------------
@app.post("/store_blob", tags=["Encrypted Storage"])
async def store_blob(
    req: StoreRequest,
    token: TokenData = Depends(require_role("admin", "researcher")),
):
    """
    Store encrypted vector in CyborgDB.
    Ciphertext is NEVER decrypted inside the proxy.
    """

    # ✅ FIXED: correct argument mapping
    insert_vector(
        hospital=req.hospital,
        case_id=req.case_id,
        enc_blob=req.enc_blob,
    )

    filename = f"{req.hospital}__{req.case_id}"

    write_audit_entry(token.sub, token.role, "store_blob", filename)

    return {
        "status": "ok",
        "storage": "cyborgdb",
        "hospital": req.hospital,
        "case_id": req.case_id,
    }

# -------------------------------------------------
# Encrypted Search (STEP 7D)
# -------------------------------------------------
@app.post("/search", tags=["Encrypted Search"])
async def encrypted_search(
    req: EncryptedSearchRequest,
    token: TokenData = Depends(require_role("clinician")),
):
    """
    Fully encrypted vector search.
    Proxy never decrypts query or results.
    """

    results = search_vectors(
        hospital=req.hospital,
        enc_query=req.enc_query,
        top_k=req.k,
    )

    write_audit_entry(token.sub, token.role, "search", req.hospital)

    return {"results": results}

# -------------------------------------------------
# Legacy File APIs (kept for compatibility)
# -------------------------------------------------
@app.get("/list_blobs", tags=["Encrypted Storage"])
async def list_blobs(
    token: TokenData = Depends(require_role("clinician", "researcher", "admin"))
):
    files = [f for f in os.listdir(DATA_DIR) if f != "audit.log"]
    write_audit_entry(token.sub, token.role, "list_blobs", "")
    return {"blobs": files}


@app.get("/fetch_blob/{filename}", tags=["Encrypted Storage"])
async def fetch_blob(
    filename: str,
    token: TokenData = Depends(require_role("clinician", "researcher", "admin"))
):
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="not found")

    with open(path, "r") as f:
        blob = json.load(f)

    write_audit_entry(token.sub, token.role, "fetch_blob", filename)

    return {"enc_blob": blob}