#!/usr/bin/env python3
"""Run Supabase migration using direct SQL execution"""

import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_migration():
    """Run the Supabase migration"""

    # Get connection details from environment
    db_url = os.getenv("SUPABASE_DATABASE_URI_SSL")

    if not db_url:
        print("No SUPABASE_DATABASE_URI_SSL found")
        return False

    try:
        print("Connecting to Supabase...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("✓ Connected to Supabase database")

        # Read migration file
        with open("supabase_migration.sql") as f:
            migration_sql = f.read()

        print("Executing migration...")
        cursor.execute(migration_sql)
        conn.commit()

        print("✓ Migration executed successfully!")

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
            print(f"\n✓ Created {len(tables)} tables in agent_state schema:")
            for schema, table in tables:
                print(f"  - {schema}.{table}")
        else:
            print("\n✗ No tables found in agent_state schema")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    if success:
        print(
            "\n🎉 Migration completed! Check your Supabase dashboard for the agent_state schema."
        )
    else:
        print("\n❌ Migration failed!")
