#!/usr/bin/env python
"""Update threads table schema to match test expectations.

This script adds the missing columns to the threads table:
- user_id: for storing owner information
- last_access: for tracking when the thread was last accessed
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("db-update")

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

def update_threads_table() -> None:
    """Update the threads table schema to match test expectations."""
    uri = get_db_uri()
    logger.info(f"Connecting to database: {uri.split('@')[1]}")

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Check if threads table exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'threads'
                );
                """)

                table_exists = cur.fetchone()[0]

                if not table_exists:
                    logger.info("Creating threads table...")
                    cur.execute("""
                    CREATE TABLE IF NOT EXISTS threads (
                        thread_id TEXT PRIMARY KEY,
                        metadata JSONB NOT NULL DEFAULT '{}',
                        user_id TEXT,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                        last_access TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    );
                    """)

                    # Create index on user_id for faster lookups
                    logger.info("Creating indexes...")
                    cur.execute("""
                    CREATE INDEX IF NOT EXISTS threads_user_id_idx ON threads (user_id);
                    """)
                    conn.commit()
                    logger.info("Threads table created successfully.")
                    return

                # Check if user_id column exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    AND table_name = 'threads' 
                    AND column_name = 'user_id'
                );
                """)

                has_user_id = cur.fetchone()[0]

                if not has_user_id:
                    logger.info("Adding user_id column...")
                    cur.execute("""
                    ALTER TABLE threads 
                    ADD COLUMN user_id TEXT;
                    
                    CREATE INDEX IF NOT EXISTS threads_user_id_idx ON threads (user_id);
                    """)

                # Check if last_access column exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_schema = 'public'
                    AND table_name = 'threads' 
                    AND column_name = 'last_access'
                );
                """)

                has_last_access = cur.fetchone()[0]

                if not has_last_access:
                    logger.info("Adding last_access column...")
                    cur.execute("""
                    ALTER TABLE threads 
                    ADD COLUMN last_access TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
                    """)

                # Make sure created_at has a default
                cur.execute("""
                SELECT column_default 
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                AND table_name = 'threads' 
                AND column_name = 'created_at';
                """)

                default_value = cur.fetchone()

                if default_value is None or default_value[0] is None:
                    logger.info("Setting default value for created_at...")
                    cur.execute("""
                    ALTER TABLE threads 
                    ALTER COLUMN created_at SET DEFAULT CURRENT_TIMESTAMP;
                    """)

                conn.commit()
                logger.info("Threads table updated successfully.")
    except Exception as e:
        logger.error(f"Database update failed: {e}")
        sys.exit(1)

def rename_table_if_needed() -> None:
    """Check if thread_metadata table exists and rename it to threads if needed."""
    uri = get_db_uri()

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Check if thread_metadata table exists
                cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'thread_metadata'
                );
                """)

                metadata_table_exists = cur.fetchone()[0]

                if metadata_table_exists:
                    # Check if threads table exists
                    cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'threads'
                    );
                    """)

                    threads_table_exists = cur.fetchone()[0]

                    if not threads_table_exists:
                        logger.info("Renaming thread_metadata table to threads...")
                        cur.execute("""
                        ALTER TABLE thread_metadata RENAME TO threads;
                        """)
                        conn.commit()
                        logger.info("Table renamed successfully.")
                    else:
                        logger.info("Both thread_metadata and threads tables exist. Keeping both for now.")
    except Exception as e:
        logger.error(f"Table rename failed: {e}")

if __name__ == "__main__":
    rename_table_if_needed()
    update_threads_table()
