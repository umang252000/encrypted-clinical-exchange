from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, List
import os, json

app = FastAPI(
    title="CyborgDB Mock (Encrypted Vectors Only)",
    description="Mock encrypted-in-use vector database (no plaintext, no decryption)"
)

# -------------------------------------------------
# Storage
# -------------------------------------------------
DATA_DIR = "/data"
os.makedirs(DATA_DIR, exist_ok=True)

# -------------------------------------------------
# Models (MATCH cyborg-proxy client)
# -------------------------------------------------
class InsertRequest(BaseModel):
    index: str              # hospital name (federation)
    id: str                 # case id
    vector: str             # ciphertext
    nonce: str              # AES-GCM nonce

class SearchRequest(BaseModel):
    index: str              # hospital name
    vector: str             # encrypted query ciphertext
    nonce: str              # nonce
    top_k: int = 5

# -------------------------------------------------
# Health
# -------------------------------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "cyborgdb-mock",
        "mode": "encrypted-only"
    }

# -------------------------------------------------
# Insert (ciphertext only)
# -------------------------------------------------
@app.post("/insert")
def insert(req: InsertRequest):
    """
    Store encrypted vector.
    Ciphertext is never decrypted.
    """
    hospital_dir = os.path.join(DATA_DIR, req.index)
    os.makedirs(hospital_dir, exist_ok=True)

    path = os.path.join(hospital_dir, f"{req.id}.json")

    with open(path, "w") as f:
        json.dump(req.dict(), f)

    return {
        "status": "stored",
        "index": req.index,
        "id": req.id
    }

# -------------------------------------------------
# Search (ciphertext-in → ciphertext-out)
# -------------------------------------------------
@app.post("/search")
def search(req: SearchRequest):
    """
    Encrypted search mock.
    Does NOT decrypt or compare vectors.
    """
    hospital_dir = os.path.join(DATA_DIR, req.index)

    if not os.path.exists(hospital_dir):
        return []

    files = sorted(os.listdir(hospital_dir))[: req.top_k]

    # Return mock ranked results
    results = []
    for i, fname in enumerate(files):
        results.append({
            "id": fname.replace(".json", ""),
            "score": round(1.0 - (i * 0.05), 3)
        })

    return results