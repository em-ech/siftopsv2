"""
Admin Authentication Module
Provides JWT-based authentication for admin dashboard access.

For production, integrate with your identity provider (Auth0, Supabase Auth, etc.)
"""

import os
import time
import hashlib
import secrets
from typing import Optional, NamedTuple
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

# JWT library (optional - use PyJWT if available)
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False


# ==================== CONFIGURATION ====================


class AuthConfig(BaseModel):
    """Authentication configuration."""
    enabled: bool = os.getenv("AUTH_ENABLED", "false").lower() == "true"
    secret_key: str = os.getenv("AUTH_SECRET_KEY", secrets.token_hex(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("AUTH_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", "7"))


auth_config = AuthConfig()

# Security scheme for swagger
security = HTTPBearer(auto_error=False)


# ==================== MODELS ====================


class TokenData(NamedTuple):
    """Decoded token data."""
    user_id: str
    tenant_id: str
    role: str
    exp: int


class TokenPair(BaseModel):
    """Access and refresh token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminUser(BaseModel):
    """Admin user representation."""
    user_id: str
    tenant_id: str
    email: str
    role: str  # owner, admin, member
    name: Optional[str] = None


# ==================== TOKEN OPERATIONS ====================


def create_access_token(user: AdminUser) -> str:
    """
    Create a JWT access token for an admin user.

    Args:
        user: AdminUser object with user details

    Returns:
        Encoded JWT token string
    """
    if not JWT_AVAILABLE:
        # Fallback to simple token if PyJWT not available
        return _create_simple_token(user)

    expire = datetime.utcnow() + timedelta(minutes=auth_config.access_token_expire_minutes)

    payload = {
        "sub": user.user_id,
        "tenant_id": user.tenant_id,
        "email": user.email,
        "role": user.role,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }

    return jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)


def create_refresh_token(user: AdminUser) -> str:
    """
    Create a JWT refresh token for token renewal.

    Args:
        user: AdminUser object

    Returns:
        Encoded JWT refresh token
    """
    if not JWT_AVAILABLE:
        return _create_simple_token(user, is_refresh=True)

    expire = datetime.utcnow() + timedelta(days=auth_config.refresh_token_expire_days)

    payload = {
        "sub": user.user_id,
        "tenant_id": user.tenant_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    return jwt.encode(payload, auth_config.secret_key, algorithm=auth_config.algorithm)


def create_token_pair(user: AdminUser) -> TokenPair:
    """Create both access and refresh tokens."""
    return TokenPair(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
        expires_in=auth_config.access_token_expire_minutes * 60,
    )


def decode_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenData if valid, None if invalid
    """
    if not JWT_AVAILABLE:
        return _decode_simple_token(token)

    try:
        payload = jwt.decode(
            token,
            auth_config.secret_key,
            algorithms=[auth_config.algorithm],
        )

        return TokenData(
            user_id=payload.get("sub"),
            tenant_id=payload.get("tenant_id"),
            role=payload.get("role", "member"),
            exp=payload.get("exp"),
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ==================== SIMPLE TOKEN FALLBACK ====================


def _create_simple_token(user: AdminUser, is_refresh: bool = False) -> str:
    """Simple token creation when PyJWT is not available."""
    expire_minutes = (
        auth_config.refresh_token_expire_days * 24 * 60
        if is_refresh
        else auth_config.access_token_expire_minutes
    )
    expire = int(time.time()) + (expire_minutes * 60)

    data = f"{user.user_id}:{user.tenant_id}:{user.role}:{expire}"
    signature = hashlib.sha256(
        f"{data}:{auth_config.secret_key}".encode()
    ).hexdigest()[:32]

    return f"{data}:{signature}"


def _decode_simple_token(token: str) -> Optional[TokenData]:
    """Decode simple token when PyJWT is not available."""
    try:
        parts = token.split(":")
        if len(parts) != 5:
            return None

        user_id, tenant_id, role, exp_str, signature = parts

        # Verify signature
        data = f"{user_id}:{tenant_id}:{role}:{exp_str}"
        expected_sig = hashlib.sha256(
            f"{data}:{auth_config.secret_key}".encode()
        ).hexdigest()[:32]

        if signature != expected_sig:
            return None

        # Check expiration
        exp = int(exp_str)
        if time.time() > exp:
            return None

        return TokenData(
            user_id=user_id,
            tenant_id=tenant_id,
            role=role,
            exp=exp,
        )
    except Exception:
        return None


# ==================== DEPENDENCIES ====================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Optional[TokenData]:
    """
    FastAPI dependency to get the current authenticated user.

    Usage:
        @router.get("/admin/dashboard")
        async def dashboard(user: TokenData = Depends(get_current_user)):
            ...
    """
    if not auth_config.enabled:
        # Auth disabled - return a default admin user for development
        return TokenData(
            user_id="dev-user",
            tenant_id="default",
            role="owner",
            exp=int(time.time()) + 3600,
        )

    if not credentials:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = decode_token(credentials.credentials)

    if not token_data:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def require_admin(
    user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    FastAPI dependency that requires admin or owner role.

    Usage:
        @router.delete("/admin/tenant")
        async def delete_tenant(user: TokenData = Depends(require_admin)):
            ...
    """
    if user.role not in ("admin", "owner"):
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return user


async def require_owner(
    user: TokenData = Depends(get_current_user),
) -> TokenData:
    """
    FastAPI dependency that requires owner role.

    Usage:
        @router.delete("/admin/tenant/delete-all")
        async def delete_all(user: TokenData = Depends(require_owner)):
            ...
    """
    if user.role != "owner":
        raise HTTPException(
            status_code=403,
            detail="Owner access required",
        )

    return user


# ==================== UTILITY FUNCTIONS ====================


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    For production, use bcrypt or argon2 instead of this simple hash.
    """
    # Simple hash verification (use bcrypt in production)
    test_hash = hashlib.sha256(plain_password.encode()).hexdigest()
    return test_hash == hashed_password


def hash_password(password: str) -> str:
    """
    Hash a password for storage.

    For production, use bcrypt or argon2 instead of this simple hash.
    """
    return hashlib.sha256(password.encode()).hexdigest()
