#!/usr/bin/env python3
"""Configure Supabase persistence with correct credentials."""

import os
from pathlib import Path

# Path to .env file
env_path = Path(__file__).parent.parent.parent / ".env"

print(f"Configuring Supabase persistence...")
print(f"Environment file: {env_path}")

# Ask user which Supabase project to use
print("\nYou have two Supabase projects configured:")
print("1. oecoeyomphckolkywbzz - Currently configured in SUPABASE_DATABASE_URI")
print("2. zkssazqhwcetsnbiuqik - Where you ran the SQL migration")

print(
    "\nTo use zkssazqhwcetsnbiuqik (where you ran the migration), you need to provide the database password."
)
print("This is NOT the JWT secret, but the actual PostgreSQL password.")
print("\nYou can find it in your Supabase dashboard under Settings > Database")

print("\nCurrent configuration will use:")
print(f"  Project: oecoeyomphckolkywbzz")
print(f"  Host: aws-0-us-east-1.pooler.supabase.com")
print(f"  Port: 6543")
print(f"  User: postgres.oecoeyomphckolkywbzz")

print("\nTo switch to zkssazqhwcetsnbiuqik, add this to your .env file:")
print(
    "SUPABASE_POSTGRES_CONNECTION=postgresql://postgres.zkssazqhwcetsnbiuqik:[YOUR_DB_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
)
print(
    "\nReplace [YOUR_DB_PASSWORD] with the actual database password from Supabase dashboard."
)
