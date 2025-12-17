from fastapi import HTTPException, Depends, Header
from jose import jwt, JWTError
from pydantic import BaseModel
import os

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

class TokenData(BaseModel):
    sub: str
    role: str

def verify_jwt(authorization: str = Header(None)) -> TokenData:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return TokenData(sub=payload["sub"], role=payload["role"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired JWT")

def require_role(*allowed_roles):
    def checker(token: TokenData = Depends(verify_jwt)):
        if token.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Access denied")
        return token
    return checker