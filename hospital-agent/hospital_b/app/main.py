import os
import json
import requests
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel, Field

# encryption / key loading
from .crypto import load_key_auto, encrypt_vector, encrypt_blob
from .kms_client import fetch_key as kms_fetch_key

# embeddings
from .embeddings import embed_texts

# utils
from .utils import load_example

CYBORG_PROXY_URL = os.getenv('CYBORG_PROXY_URL', 'http://cyborg-proxy:8000')
KEY_PATH = os.getenv('KEY_PATH', '/keys/hospital_b.key')
HOSPITAL_NAME = os.getenv('HOSPITAL_NAME', 'HospitalB')

app = FastAPI(
    title=f"{HOSPITAL_NAME} Agent",
    description="Encrypted hospital-side agent for secure clinical data ingestion",
    version="1.0.0",
)

# -------------------------------------------------------
# SYSTEM ENDPOINTS
# -------------------------------------------------------
@app.get("/", tags=["System"])
def root():
    return {
        "service": f"{HOSPITAL_NAME} Agent",
        "role": "Encrypted data producer",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "ok",
        "service": HOSPITAL_NAME,
    }


# -------------------------------------------------------
# AUTHENTICATED POST TO PROXY (Option B)
# -------------------------------------------------------
def post_to_proxy(payload):
    proxy_url = os.getenv("CYBORG_PROXY_URL", "http://cyborg-proxy:8000")
    token = os.getenv("HOSPITAL_API_TOKEN", "")

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = requests.post(
        f"{proxy_url}/store_blob",
        json=payload,
        headers=headers,
        timeout=10,
    )
    r.raise_for_status()
    return r


# -------------------------------------------------------
# KEY LOADING (FILE OR KMS)
# -------------------------------------------------------
try:
    KEY = load_key_auto(KEY_PATH, kms_fetcher=kms_fetch_key)
except Exception as e:
    raise RuntimeError(f"Failed to load key: {e}")


# -------------------------------------------------------
# MODELS
# -------------------------------------------------------
class Case(BaseModel):
    id: str
    text: str
    metadata: dict = Field(default_factory=dict)


# -------------------------------------------------------
# INGEST EXAMPLE (AUTH + ENCRYPT + POST)
# -------------------------------------------------------
@app.post("/ingest_example", tags=["Ingest"])
def ingest_example():

    # 1) Load example JSON
    plain = load_example()

    # 2) Use loaded KEY (FILE or KMS)
    key = KEY

    # 3) Encrypt example
    enc = encrypt_blob(key, plain)

    # 4) Prepare payload
    case_id = plain.get("case_id", "case-001")
    payload = {
        "hospital": HOSPITAL_NAME,
        "case_id": case_id,
        "enc_blob": enc,
    }

    # 5) Send to proxy with JWT admin token
    r = post_to_proxy(payload)

    return {
        "status": "ok",
        "sent_to_proxy": True,
        "proxy_response": r.json(),
    }


# -------------------------------------------------------
# INGEST SINGLE CASE
# -------------------------------------------------------
@app.post("/ingest_case", tags=["Ingest"])
async def ingest_case(case: Case):
    try:
        # 1) Embed text
        embs = embed_texts([case.text])
        vec = embs[0]

        # 2) Build payload for encryption
        payload_obj = {
            "vector": vec,
            "metadata": case.metadata,
        }
        vec_bytes = json.dumps(payload_obj).encode("utf-8")

        # 3) Encrypt using loaded KEY
        enc = encrypt_vector(KEY, vec_bytes)

        payload = {
            "hospital": HOSPITAL_NAME,
            "case_id": case.id,
            "enc_blob": enc,
        }

        # 4) Send to proxy
        r = post_to_proxy(payload)
        return r.json()

    except Exception as e:
        return {
            "error": "proxy_store_failed",
            "details": str(e),
        }


# -------------------------------------------------------
# INGEST CSV
# -------------------------------------------------------
@app.post("/ingest_csv", tags=["Ingest"])
async def ingest_csv(file: UploadFile = File(...)):
    content = (await file.read()).decode("utf-8")
    lines = [l.strip() for l in content.split("\n") if l.strip()]
    results = []

    for idx, line in enumerate(lines):
        case = Case(
            id=f"{HOSPITAL_NAME}-{idx}",
            text=line,
        )
        res = await ingest_case(case)
        results.append(res)

    return {
        "stored": len(results),
        "details": results,
    }

@app.post("/encrypt_query")
def encrypt_query(text: str):
    """
    Embed + encrypt clinician query.
    Plaintext NEVER leaves hospital boundary.
    """
    emb = embed_texts([text])[0]

    payload = {
        "vector": emb
    }

    vec_bytes = json.dumps(payload).encode("utf-8")
    enc = encrypt_vector(KEY, vec_bytes)

    return enc