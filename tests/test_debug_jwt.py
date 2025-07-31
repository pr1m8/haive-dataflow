# debug_jwt.py
import os
from datetime import datetime, timedelta

import jwt

# Print environment variables (with secrets partially masked)
jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "")
print(f"JWT Secret: {jwt_secret}")
if jwt_secret:
    print(f"JWT Secret (first/last 3 chars): {jwt_secret[:3]}...{jwt_secret[-3:]}")
    print(f"JWT Secret length: {len(jwt_secret)}")
else:
    print("WARNING: SUPABASE_JWT_SECRET is not set")

# Test if the secret is valid for JWT operations
test_payload = {
    "sub": "test-user",
    "exp": datetime.utcnow() + timedelta(minutes=5),
    "iat": datetime.utcnow(),
}

try:
    # Try to create a JWT with this secret
    token = jwt.encode(test_payload, jwt_secret, algorithm="HS256")
    print(f"Successfully created test token: {token[:10]}...")

    # Try to decode the token we just created
    decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    print("Successfully decoded test token!")
    print("This confirms the JWT secret is valid for JWT operations")
except Exception as e:
    print(f"ERROR testing JWT operations: {e!s}")
    print("This suggests the JWT secret might not be valid")

# For comparison, print the beginning of the token from logs
print("\nComparing with your current token:")
token_from_logs = "eyJ"  # This is what we saw in the logs
if jwt_secret.startswith(token_from_logs):
    print("WARNING: Your JWT secret appears to be a JWT token itself, not a raw secret")
else:
    print("Your JWT secret does not appear to be a JWT token, which is good")
