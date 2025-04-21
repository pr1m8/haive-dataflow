#!/bin/bash
# Temporary debugging modifications for haive-core tests

# Locate the test file
TEST_FILE="packages/haive-core/tests/engine/agent/test_persistence.py"

# Add debug prints to the failing tests
sed -i '/def test_register_thread_with_auth_info/a\        print("\nDEBUG: In test_register_thread_with_auth_info\n")' $TEST_FILE
sed -i '/def test_prepare_for_agent_run/a\        print("\nDEBUG: In test_prepare_for_agent_run\n")' $TEST_FILE
sed -i '/def test_list_threads_with_user_id/a\        print("\nDEBUG: In test_list_threads_with_user_id\n")' $TEST_FILE

# Add more detailed assertion messages
sed -i 's/assert len(threads) == 1/assert len(threads) == 1, f"Expected 1 thread for user {user_id1}, got {len(threads)}"/' $TEST_FILE

echo "Test file patched for debugging. Run the tests again with: cd packages/haive-core && python -m pytest tests/engine/agent/test_persistence.py::TestPersistenceManager::test_list_threads_with_user_id -v"
