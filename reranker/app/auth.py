# reranker/app/auth.py

from fastapi import Request, HTTPException, Depends
from jose import jwt, JWTError
import os
from dataclasses import dataclass

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")


@dataclass
class TokenData:
    sub: str
    role: str


async def verify_jwt(request: Request) -> TokenData:
    """
    Verifies JWT from Authorization header.
    Used by /whoami and shared RBAC logic.
    """
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
        role = payload.get("role")

        if not sub or not role:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        return TokenData(sub=sub, role=role)

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_roles(*allowed_roles):
    """
    RBAC dependency factory.
    Example:
        Depends(require_roles("clinician"))
    """
    async def _require(token: TokenData = Depends(verify_jwt)):
        if token.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return token

    return _require
