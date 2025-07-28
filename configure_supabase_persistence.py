"""Configure Supabase Persistence - Configure Supabase Persistence module

TODO: Add comprehensive description of configure supabase persistence functionality.

This module provides core functionality for the Haive AI Agent Framework.

Key Components:
    - Core module components (see source code)

Example:
    Basic usage::

        from packages.haive-dataflow import None

        # Create instance
        instance = None(name='example')

        # Use the core functionality
        result = instance.None('input_data')

        print(f"Result: {result}")

Advanced Usage:
    TODO: Add advanced core functionality example

See Also:
    TODO: List related modules

Notes:
    TODO: Add implementation notes and caveats
"""

#!/usr/bin/env python3
"""Configure Supabase persistence with correct credentials."""

from pathlib import Path

# Path to .env file
env_path = Path(__file__).parent.parent.parent / ".env"

print("Configuring Supabase persistence...")
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
print("  Project: oecoeyomphckolkywbzz")
print("  Host: aws-0-us-east-1.pooler.supabase.com")
print("  Port: 6543")
print("  User: postgres.oecoeyomphckolkywbzz")

print("\nTo switch to zkssazqhwcetsnbiuqik, add this to your .env file:")
print(
    "SUPABASE_POSTGRES_CONNECTION=postgresql://postgres.zkssazqhwcetsnbiuqik:[YOUR_DB_PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres"
)
print(
    "\nReplace [YOUR_DB_PASSWORD] with the actual database password from Supabase dashboard."
)
