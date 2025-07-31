# check_env.py
import os

from dotenv import load_dotenv

load_dotenv()

env_vars = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_KEY",
    "SUPABASE_JWT_SECRET",
    "TEST_SUPABASE_TOKEN",
]

print("Checking environment variables:")
for var in env_vars:
    value = os.getenv(var)
    if value:
        # Only show first few characters for security
        print(f"{var}: {value[:5]}...")
    else:
        print(f"{var}: NOT SET")
