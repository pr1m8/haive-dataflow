#!/usr/bin/env python3
"""Generate a valid JWT token for testing."""

import os
from datetime import datetime, timedelta

import jwt

# Get the secret from environment
secret = os.getenv(
    "SUPABASE_JWT_SECRET",
    "J89XqGf7hDkKejOK1n02TKVT78TtncD3gP0TH68N4AV1H87viAt9EhQxVp0mfUxkBNHowVCng2okkmPHYZpiKA==",
)

# Create token payload
payload = {
    "aud": "authenticated",
    "exp": datetime.utcnow() + timedelta(hours=24),
    "iat": datetime.utcnow(),
    "iss": "https://zkssazqhwcetsnbiuqik.supabase.co/auth/v1",
    "sub": "test-user-123",
    "email": "test@user.com",
    "role": "authenticated",
    "app_metadata": {"provider": "email", "providers": ["email"]},
    "user_metadata": {
        "email": "test@user.com",
        "email_verified": True,
        "phone_verified": False,
        "sub": "test-user-123",
    },
    "session_id": "test-session-123",
    "is_anonymous": False,
}

# Generate token
token = jwt.encode(
    payload, secret, algorithm="HS256", headers={"kid": "8Gol6XEitfGLrnol"}
)

print(f"Generated token: {token}")
print(f"\nPayload:")
print(f"  User ID: {payload['sub']}")
print(f"  Email: {payload['email']}")
print(f"  Expires: {payload['exp']}")
