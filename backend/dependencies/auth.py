import os
import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError, jwk
from functools import lru_cache

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL")


@lru_cache(maxsize=1)
def get_jwks():
    """Fetch and cache the JWKS from Supabase."""
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL not configured")

    jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()


def get_public_key(token: str):
    """Get the public key for verifying the token."""
    jwks = get_jwks()

    # Get the key ID from the token header
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")

    # Find the matching key in JWKS
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return jwk.construct(key)

    raise ValueError(f"Public key not found for kid: {kid}")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Extracts and verifies the Supabase JWT from the Authorization header.
    Returns the user_id (sub claim) if valid.

    Raises HTTPException 401 if token is missing, invalid, or expired.
    """
    if not SUPABASE_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL not configured",
        )

    token = credentials.credentials

    try:
        # Get public key and verify token
        public_key = get_public_key(token)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience="authenticated",
        )

        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

        return user_id

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
        )
