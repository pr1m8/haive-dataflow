#!/usr/bin/env python
"""Fix remaining issues with the persistence manager tests.

This script addresses issues with:
1. Debug test failures and add database modifications to fix them
2. Clean up data that might be causing count mismatches
3. Find and fix metadata JSON serialization in persistence manager
"""

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

def examine_db_state():
    """Examine the database state to understand what's happening."""
    uri = get_db_uri()
    logger.info(f"Connecting to database: {uri.split('@')[1]}")

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Check existing test-user-id rows
                cur.execute("SELECT thread_id, user_id FROM threads WHERE user_id = 'test-user-id'")
                test_user_rows = cur.fetchall()
                logger.info(f"Found {len(test_user_rows)} rows with user_id = 'test-user-id'")
                for row in test_user_rows:
                    logger.info(f"Thread: {row[0]}, User: {row[1]}")

                # Check test-user-id-1 and test-user-id-2 rows
                cur.execute("SELECT thread_id, user_id FROM threads WHERE user_id = 'test-user-id-1'")
                test_user1_rows = cur.fetchall()
                logger.info(f"Found {len(test_user1_rows)} rows with user_id = 'test-user-id-1'")

                cur.execute("SELECT thread_id, user_id FROM threads WHERE user_id = 'test-user-id-2'")
                test_user2_rows = cur.fetchall()
                logger.info(f"Found {len(test_user2_rows)} rows with user_id = 'test-user-id-2'")

                # Get a sample of metadata
                cur.execute("SELECT thread_id, metadata FROM threads LIMIT 5")
                metadata_samples = cur.fetchall()
                logger.info("Metadata samples:")
                for row in metadata_samples:
                    logger.info(f"Thread: {row[0]}, Metadata type: {type(row[1])}, Value: {row[1]}")
    except Exception as e:
        logger.error(f"Failed to examine database state: {e}")

def clean_test_specific_data():
    """Clean up data specific to problematic tests to ensure a clean slate."""
    uri = get_db_uri()

    try:
        with psycopg.connect(uri) as conn:
            with conn.cursor() as cur:
                # Delete all rows with test user IDs to ensure count tests work properly
                for user_id in ["test-user-id", "test-user-id-1", "test-user-id-2"]:
                    cur.execute("DELETE FROM threads WHERE user_id = %s", (user_id,))
                    rows_deleted = cur.rowcount
                    logger.info(f"Deleted {rows_deleted} rows with user_id = '{user_id}'")

                conn.commit()
    except Exception as e:
        logger.error(f"Failed to clean test-specific data: {e}")

def modify_haive_core_persistence_manager():
    """This is a debugging function to explain what changes are needed in the PersistenceManager.
    
    We can't directly modify the haive-core code here, but we can print out what changes are needed.
    """
    logger.info("=== REQUIRED FIXES IN HAIVE-CORE PERSISTENCE MANAGER ===")
    logger.info("1. In the register_thread method, ensure auth_info is properly JSON serialized:")
    logger.info("   - Find the SQL INSERT statement where metadata is inserted")
    logger.info("   - Make sure it's using json.dumps(metadata) before passing to the database")
    logger.info("   - Look for: 'INSERT INTO threads (thread_id, metadata, user_id)...'")
    logger.info("")
    logger.info("2. In the prepare_for_agent_run method:")
    logger.info("   - Check the return value - it should be a tuple of (config, thread_id)")
    logger.info("   - Make sure thread registration is working correctly")
    logger.info("")
    logger.info("3. In the list_threads method when filtering by user_id:")
    logger.info("   - Check if there are any issues with the SQL WHERE clause")
    logger.info("   - Add debug logging to see what's being returned")
    logger.info("==========================================================")

def create_test_patch_script():
    """Create a shell script to patch the haive-core tests temporarily for debugging."""
    patch_script = """#!/bin/bash
# Temporary debugging modifications for haive-core tests

# Locate the test file
TEST_FILE="packages/haive-core/tests/engine/agent/test_persistence.py"

# Add debug prints to the failing tests
sed -i '/def test_register_thread_with_auth_info/a\\        print("\\nDEBUG: In test_register_thread_with_auth_info\\n")' $TEST_FILE
sed -i '/def test_prepare_for_agent_run/a\\        print("\\nDEBUG: In test_prepare_for_agent_run\\n")' $TEST_FILE
sed -i '/def test_list_threads_with_user_id/a\\        print("\\nDEBUG: In test_list_threads_with_user_id\\n")' $TEST_FILE

# Add more detailed assertion messages
sed -i 's/assert len(threads) == 1/assert len(threads) == 1, f"Expected 1 thread for user {user_id1}, got {len(threads)}"/' $TEST_FILE

echo "Test file patched for debugging. Run the tests again with: cd packages/haive-core && python -m pytest tests/engine/agent/test_persistence.py::TestPersistenceManager::test_list_threads_with_user_id -v"
"""

    with open("debug_haive_core_tests.sh", "w") as f:
        f.write(patch_script)

    os.chmod("debug_haive_core_tests.sh", 0o755)
    logger.info("Created debug_haive_core_tests.sh script")

def main():
    """Run all fix operations."""
    logger.info("Examining current database state...")
    examine_db_state()

    logger.info("\nCleaning up test-specific data...")
    clean_test_specific_data()

    logger.info("\nProviding guidance for fixing PersistenceManager in haive-core...")
    modify_haive_core_persistence_manager()

    logger.info("\nCreating test patch script for debugging...")
    create_test_patch_script()

    logger.info("\nAll done! Here's what you should do next:")
    logger.info("1. Run the debug_haive_core_tests.sh script to add debugging to tests")
    logger.info("2. Make the recommended changes to the haive-core PersistenceManager")
    logger.info("3. Run the tests again with more verbose output to diagnose further")

if __name__ == "__main__":
    main()
