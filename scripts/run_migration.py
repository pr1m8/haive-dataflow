#!/usr/bin/env python3
"""Run Supabase migration using direct SQL execution."""

import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_migration():
    """Run the Supabase migration."""
    # Get connection details from environment
    db_url = os.getenv("SUPABASE_DATABASE_URI_SSL")

    if not db_url:
        return False

    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Read migration file
        with open("supabase_migration.sql") as f:
            migration_sql = f.read()

        cursor.execute(migration_sql)
        conn.commit()

        # Verify the schema was created
        cursor.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = 'agent_state'
            ORDER BY table_name
        """
        )

        tables = cursor.fetchall()
        if tables:
            for _schema, _table in tables:
                pass
        else:
            pass

        cursor.close()
        conn.close()

        return True

    except Exception:
        return False


if __name__ == "__main__":
    success = run_migration()
    if success:
        pass
    else:
        pass
