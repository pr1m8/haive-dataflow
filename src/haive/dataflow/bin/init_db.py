#!/usr/bin/env python
"""Database initialization script for haive-dataflow.

This script initializes the PostgreSQL database tables required for thread
persistence and other functionality.
"""

import logging
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("db-init")

try:
    import psycopg
    from psycopg_pool import ConnectionPool
except ImportError:
    logger.error("Required packages not found. Install with: pip install psycopg psycopg_pool")
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

def init_database() -> None:
    """Initialize database tables."""
    uri = get_db_uri()
    logger.info(f"Connecting to database: {uri.split('@')[1]}")

    try:
        # Create connection pool
        with ConnectionPool(uri) as pool:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    # Create thread metadata table if not exists
                    logger.info("Creating thread_metadata table...")
                    cur.execute("""
                    CREATE TABLE IF NOT EXISTS thread_metadata (
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
                    CREATE INDEX IF NOT EXISTS thread_metadata_user_id_idx ON thread_metadata (user_id);
                    """)

                    conn.commit()
                    logger.info("Database initialization complete.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()
