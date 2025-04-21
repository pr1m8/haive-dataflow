#!/usr/bin/env python
"""Fix issues with the database schema for tests.

This script addresses several issues:
1. Ensures metadata is properly stored as JSON
2. Adds cascade delete to foreign key constraints
3. Cleans up test data from previous test runs
"""

import json
import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("db-fix")

try:
    import psycopg
except ImportError:
    logger.error("Required packages not found. Install with: pip install psycopg")
    sys.exit(1)

def get_db_uri() -> str:
    """Get database URI from environment variables."""
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "postgres")
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    ssl_mode = os.environ.get("POSTGRES_SSL_MODE", "prefer")

    return f"postgresql://{user}:{password}@{host}:{port}/{db}?sslmode={ssl_mode}"

def fix_json_serialization() -> None:
    """Fix JSON serialization issues in the metadata column."""
    uri = get_db_uri()
    logger.info(f"Connecting to database: {uri.split('@')[1]}")

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Check if the table exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'threads'
                );
                """)

                if not cur.fetchone()[0]:
                    logger.info("Threads table does not exist. Skipping JSON fix.")
                    return

                # Get all rows with metadata
                cur.execute("SELECT thread_id, metadata FROM threads")
                rows = cur.fetchall()

                for row in rows:
                    thread_id, metadata = row

                    # Skip if metadata is already a string
                    if isinstance(metadata, str):
                        continue

                    # If metadata is a dict or other type, serialize it to JSON
                    if metadata is not None:
                        try:
                            # Try to convert to JSON string if it's not already
                            if not isinstance(metadata, str):
                                json_metadata = json.dumps(metadata)
                                cur.execute(
                                    "UPDATE threads SET metadata = %s WHERE thread_id = %s",
                                    (json_metadata, thread_id)
                                )
                                logger.info(f"Fixed JSON serialization for thread {thread_id}")
                        except Exception as e:
                            logger.warning(f"Could not fix metadata for thread {thread_id}: {e}")

                conn.commit()
                logger.info("JSON serialization issues fixed")
    except Exception as e:
        logger.error(f"Failed to fix JSON serialization: {e}")

def handle_foreign_key_constraints() -> None:
    """Add ON DELETE CASCADE to foreign key constraints."""
    uri = get_db_uri()

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Check if the checkpoints table exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'checkpoints'
                );
                """)

                if not cur.fetchone()[0]:
                    logger.info("Checkpoints table does not exist. Skipping foreign key fix.")
                    return

                # Get constraint name
                cur.execute("""
                SELECT constraint_name
                FROM information_schema.table_constraints
                WHERE table_schema = 'public'
                AND table_name = 'checkpoints'
                AND constraint_type = 'FOREIGN KEY';
                """)

                constraints = cur.fetchall()

                if not constraints:
                    logger.info("No foreign key constraints found.")
                    return

                for constraint in constraints:
                    constraint_name = constraint[0]

                    # Drop the constraint
                    logger.info(f"Dropping constraint {constraint_name}")
                    cur.execute(f"ALTER TABLE checkpoints DROP CONSTRAINT {constraint_name}")

                    # Create new constraint with ON DELETE CASCADE
                    logger.info("Creating new constraint with ON DELETE CASCADE")
                    cur.execute("""
                    ALTER TABLE checkpoints
                    ADD CONSTRAINT fk_checkpoints_thread
                    FOREIGN KEY (thread_id) REFERENCES threads(thread_id)
                    ON DELETE CASCADE;
                    """)

                conn.commit()
                logger.info("Foreign key constraints updated with ON DELETE CASCADE")
    except Exception as e:
        logger.error(f"Failed to update foreign key constraints: {e}")

def clean_test_data() -> None:
    """Clean up test data from previous test runs."""
    uri = get_db_uri()

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Check if the threads table exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'threads'
                );
                """)

                if not cur.fetchone()[0]:
                    logger.info("Threads table does not exist. Skipping cleanup.")
                    return

                # Delete test data
                cur.execute("DELETE FROM threads WHERE thread_id LIKE 'test-%'")
                rows_deleted = cur.rowcount

                # Delete specific problematic thread
                cur.execute("DELETE FROM threads WHERE thread_id = 'test-schema-123'")
                rows_deleted += cur.rowcount

                conn.commit()
                logger.info(f"Deleted {rows_deleted} test threads")
    except Exception as e:
        logger.error(f"Failed to clean up test data: {e}")

if __name__ == "__main__":
    clean_test_data()
    fix_json_serialization()
    handle_foreign_key_constraints()
