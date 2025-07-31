# debug_jwt.py
import os
from datetime import datetime, timedelta

import jwt

# Print environment variables (with secrets partially masked)
jwt_secret = os.getenv("SUPABASE_JWT_SECRET", "")
if jwt_secret:
    pass
else:
    pass

# Test if the secret is valid for JWT operations
test_payload = {
    "sub": "test-user",
    "exp": datetime.utcnow() + timedelta(minutes=5),
    "iat": datetime.utcnow(),
}

try:
    # Try to create a JWT with this secret
    token = jwt.encode(test_payload, jwt_secret, algorithm="HS256")

    # Try to decode the token we just created
    decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
except Exception:
    pass

# For comparison, print the beginning of the token from logs
token_from_logs = "eyJ"  # This is what we saw in the logs
if jwt_secret.startswith(token_from_logs):
    pass
else:
    pass
