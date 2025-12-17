from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List

# Shared auth (single source of truth)
from .auth import verify_jwt, require_roles, TokenData

# -------------------------------------------------------
# APP METADATA (Swagger polish)
# -------------------------------------------------------
app = FastAPI(
    title="Privacy-Preserving Reranker",
    description="""
### 🧠 Encrypted-in-Use Ranking Service

This service performs **local reranking** over encrypted clinical case references.

**Security guarantees**
- JWT authentication
- Role-Based Access Control (RBAC)
- Clinician-only access
- No plaintext data stored
- No decrypted vectors leave the process

Designed for enterprise & healthcare compliance demos.
""",
    version="1.0.0",
)

# -------------------------------------------------------
# REQUEST MODELS
# -------------------------------------------------------
class RerankRequest(BaseModel):
    case_ids: List[str]
    query: str

# -------------------------------------------------------
# RERANK ENDPOINT (CLINICIAN ONLY)
# -------------------------------------------------------
@app.post(
    "/rerank",
    tags=["Reranking"],
    summary="Clinician-only encrypted reranking",
)
async def rerank(
    req: RerankRequest,
    token: TokenData = Depends(require_roles("clinician")),
):
    """
    Secure reranking endpoint.

    Only users with **role=clinician** may access this endpoint.
    """

    # Placeholder reranking logic
    # (real system would decrypt locally + score vectors)
    reranked = list(reversed(req.case_ids))

    return {
        "actor": token.sub,
        "role": token.role,
        "query": req.query,
        "reranked": reranked,
    }

# -------------------------------------------------------
# SYSTEM ENDPOINTS
# -------------------------------------------------------
@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
)
def health():
    return {
        "status": "ok",
        "service": "reranker",
    }

@app.get(
    "/",
    tags=["System"],
    summary="Service information",
)
def root():
    return {
        "service": "Privacy-Preserving Reranker",
        "description": "Clinician-only encrypted-in-use ranking service",
        "docs": "/docs",
        "health": "/health",
    }

# -------------------------------------------------------
# AUTH DEBUG / INTROSPECTION
# -------------------------------------------------------
@app.get(
    "/whoami",
    tags=["Auth"],
    summary="Return identity from JWT",
)
def whoami(token: TokenData = Depends(verify_jwt)):
    return {
        "sub": token.sub,
        "role": token.role,
        "service": "reranker",
    }