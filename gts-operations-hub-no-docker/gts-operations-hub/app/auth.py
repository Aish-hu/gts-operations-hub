"""Optional Keycloak JWT validation; local demo defaults to authentication disabled."""
import os
from functools import lru_cache
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt import PyJWKClient, decode
from jwt.exceptions import PyJWTError

bearer = HTTPBearer(auto_error=False)

@lru_cache
def jwks_client(url: str):
    return PyJWKClient(url)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if os.getenv("AUTH_ENABLED", "false").lower() != "true":
        return {"sub": "local-developer", "preferred_username": "local-dev"}
    if not credentials:
        raise HTTPException(status_code=401, detail="Bearer token required")
    issuer = os.getenv("KEYCLOAK_ISSUER", "http://localhost:8081/realms/gts")
    jwks_url = os.getenv("KEYCLOAK_JWKS_URL", issuer.rstrip("/") + "/protocol/openid-connect/certs")
    try:
        key = jwks_client(jwks_url).get_signing_key_from_jwt(credentials.credentials)
        claims = decode(credentials.credentials, key.key, algorithms=["RS256"], issuer=issuer,
                        audience=os.getenv("KEYCLOAK_AUDIENCE", "gts-api"))
        return claims
    except (PyJWTError, ValueError, Exception) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired access token") from exc
