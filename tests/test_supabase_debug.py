# debug_supabase.py
import asyncio
import json
import logging
import os
import sys
import traceback
import uuid
from decimal import Decimal

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("debug_supabase")

# Add specific module loggers
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)


def print_separator():
    """Print a separator line."""


async def safe_import(module_path, class_name=None):
    """Safely import a module or class with detailed error reporting."""
    try:
        module = __import__(module_path, fromlist=[class_name] if class_name else ["*"])
        if class_name:
            return getattr(module, class_name)
        return module
    except ImportError as e:
        logger.exception(f"Import error: {e}")
        logger.exception(f"Could not import {class_name or module_path}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return None
    except AttributeError as e:
        logger.exception(f"Attribute error: {e}")
        logger.exception(f"Could not find {class_name} in {module_path}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return None


async def run_with_error_handling(func_name, func, *args, **kwargs):
    """Run a function with detailed error handling."""
    print_separator()
    logger.info(f"RUNNING: {func_name}")

    try:
        result = await func(*args, **kwargs)
        logger.info(f"COMPLETED: {func_name} - Result: {result}")
        return result
    except Exception as e:
        logger.exception(f"ERROR in {func_name}: {e}")
        logger.exception(f"Stack trace:\n{traceback.format_exc()}")
        return None


async def test_config():
    """Test environment configuration."""
    logger.info("TESTING ENVIRONMENT CONFIGURATION")

    # Check all required environment variables
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_JWT_SECRET",
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
        return False

    # Import environment config
    get_supabase_client_config = await safe_import(
        "haive.dataflow.config.environment", "get_supabase_client_config"
    )
    get_supabase_server_config = await safe_import(
        "haive.dataflow.config.environment", "get_supabase_server_config"
    )

    if not get_supabase_client_config or not get_supabase_server_config:
        return False

    try:
        # Test client config
        client_config = get_supabase_client_config()
        logger.info(f"Supabase URL: {client_config.url}")
        logger.info(
            f"Anon key present: {'Yes' if client_config.anon_key.get_secret_value() else 'No'}"
        )

        # Test server config
        server_config = get_supabase_server_config()
        logger.info(f"Supabase URL: {server_config.url}")
        logger.info(
            f"Service key present: {'Yes' if server_config.service_role_key.get_secret_value() else 'No'}"
        )
        logger.info(
            f"JWT secret present: {'Yes' if server_config.jwt_secret.get_secret_value() else 'No'}"
        )

        return True
    except Exception as e:
        logger.exception(f"Error in config test: {e}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return False


async def test_supabase_connection():
    """Test basic Supabase connection."""
    logger.info("TESTING SUPABASE CONNECTION")

    try:
        # Try to import supabase client
        from supabase import create_client

        # Get credentials from environment
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")

        # Create client
        logger.info("Creating Supabase client...")
        client = create_client(supabase_url, supabase_key)

        # Test simple query
        logger.info("Testing query...")
        response = client.from_("threads").select("*").limit(1).execute()
        logger.info(f"Response type: {type(response)}")
        logger.info(f"Response raw: {response}")
        # logger.info(f"Response status: {getattr(response, 'status_code', 'unknown')}")
        logger.info(f"Response data: {getattr(response, 'data', 'unknown')}")

        # Check response
        # logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response data: {json.dumps(response.data)}")

        return True
    except Exception as e:
        logger.exception(f"Error connecting to Supabase: {e}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return False


async def test_auth():
    """Test authentication functionality."""
    logger.info("TESTING AUTH FUNCTIONALITY")

    # Get a test token from environment
    test_token = os.getenv("TEST_SUPABASE_TOKEN")
    if not test_token:
        logger.error("No test token available. Set TEST_SUPABASE_TOKEN in .env file")
        return False

    # Import SupabaseAuth
    SupabaseAuth = await safe_import("haive.dataflow.auth.supabase", "SupabaseAuth")
    if not SupabaseAuth:
        return False

    try:
        # Initialize auth
        logger.info("Initializing SupabaseAuth...")
        auth = SupabaseAuth()

        # Verify token
        logger.info(f"Verifying token: {test_token[:10]}...")
        payload = auth.verify_token(test_token)

        if not payload:
            logger.error("Token verification failed")
            return False

        logger.info(f"Token payload: {json.dumps(payload)}")

        # Extract user ID
        user_id = auth.get_user_id(test_token)
        if not user_id:
            logger.error("Failed to extract user ID from token")
            return False

        logger.info(f"Auth test successful - User ID: {user_id}")
        return user_id
    except Exception as e:
        logger.exception(f"Error testing auth: {e}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return False


async def test_credits(user_id):
    """Test credits functionality."""
    logger.info("TESTING CREDITS FUNCTIONALITY")

    # Import classes
    CreditsManager = await safe_import("haive_dataflow.auth.credits", "CreditsManager")
    UsageRecord = await safe_import("haive_dataflow.auth.credits", "UsageRecord")

    if not CreditsManager or not UsageRecord:
        return False

    try:
        # Initialize credits manager
        credits_manager = CreditsManager()

        # Check if user has any credits
        logger.info("Checking credits...")
        has_credits = await credits_manager.check_credits(user_id)
        logger.info(f"User has credits: {has_credits}")

        # Log a small usage record for testing
        logger.info("Logging usage...")
        usage = UsageRecord(
            agent_id="test-agent",
            user_id=user_id,
            conversation_id="test-conversation",
            token_count=10,
            cost=Decimal("0.0001"),
        )

        success = await credits_manager.log_usage(usage)
        logger.info(f"Logged usage: {success}")

        return success
    except Exception as e:
        logger.exception(f"Error testing credits: {e}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return False


async def test_conversation(user_id):
    """Test conversation functionality."""
    logger.info("TESTING CONVERSATION FUNCTIONALITY")

    # Import classes
    ConversationManager = await safe_import(
        "haive_dataflow.persistence.conversations", "ConversationManager"
    )
    ConversationMetadata = await safe_import(
        "haive_dataflow.persistence.conversations", "ConversationMetadata"
    )

    if not ConversationManager or not ConversationMetadata:
        return False

    try:
        # Initialize conversation manager
        logger.info("Initializing ConversationManager...")
        conversation_manager = ConversationManager()

        # Create a test conversation
        logger.info("Creating test conversation...")
        metadata = ConversationMetadata(
            agent_id="test-agent", title=f"Test Conversation {uuid.uuid4()}"
        )

        result = await conversation_manager.create_conversation(user_id, metadata)
        if not result:
            logger.error("Failed to create conversation")
            return False

        logger.info(f"Created conversation: {result}")
        thread_id = result.get("thread_id")

        # Get the conversation we just created
        logger.info(f"Retrieving conversation {thread_id}...")
        conversation = await conversation_manager.get_conversation(thread_id, user_id)
        if not conversation:
            logger.error("Failed to retrieve conversation")
            return False

        logger.info(f"Retrieved conversation: {conversation}")

        # List conversations for user
        logger.info("Listing all conversations...")
        conversations = await conversation_manager.list_conversations(user_id)
        logger.info(f"Found {len(conversations)} conversations for user")

        return thread_id
    except Exception as e:
        logger.exception(f"Error testing conversations: {e}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return False


async def test_persistence(user_id, thread_id):
    """Test persistence functionality."""
    logger.info("TESTING PERSISTENCE FUNCTIONALITY")

    # Import class
    SupabasePersistence = await safe_import(
        "haive_dataflow.persistence.supabase_adapter", "SupabasePersistence"
    )
    if not SupabasePersistence:
        return False

    try:
        # Initialize persistence
        logger.info("Initializing SupabasePersistence...")
        persistence = SupabasePersistence()

        # Test state update
        logger.info("Updating state...")
        test_data = {
            "messages": [{"role": "user", "content": "Hello, this is a test message"}],
            "metadata": {"test": True, "timestamp": str(uuid.uuid4())},
        }

        success = await persistence.update_state(thread_id, user_id, test_data)
        if not success:
            logger.error("Failed to update state")
            return False

        logger.info("Successfully updated state")

        # Get state back
        logger.info("Retrieving state...")
        state = await persistence.get_state(thread_id, user_id)
        if not state:
            logger.error("Failed to retrieve state")
            return False

        logger.info(f"Retrieved state: {state}")
        return True
    except Exception as e:
        logger.exception(f"Error testing persistence: {e}")
        logger.exception(f"Stack trace: {traceback.format_exc()}")
        return False


async def main():
    """Run all tests with error handling."""
    logger.info("Starting Supabase debugging tests")

    # Test config
    config_result = await run_with_error_handling("test_config", test_config)
    if not config_result:
        logger.error("Configuration test failed. Stopping further tests.")
        return

    # Test Supabase connection
    connection_result = await run_with_error_handling(
        "test_supabase_connection", test_supabase_connection
    )
    if not connection_result:
        logger.error("Supabase connection test failed. Stopping further tests.")
        return

    # Test auth
    user_id = await run_with_error_handling("test_auth", test_auth)
    if not user_id:
        logger.error("Auth test failed. Stopping further tests.")
        return

    # Test credits
    credits_result = await run_with_error_handling(
        "test_credits", test_credits, user_id
    )

    # Test conversation
    thread_id = await run_with_error_handling(
        "test_conversation", test_conversation, user_id
    )
    if not thread_id:
        logger.error("Conversation test failed. Stopping further tests.")
        return

    # Test persistence
    persistence_result = await run_with_error_handling(
        "test_persistence", test_persistence, user_id, thread_id
    )

    # Overall results
    print_separator()
    logger.info("TEST RESULTS SUMMARY:")
    logger.info(f"Config: {'SUCCESS' if config_result else 'FAILED'}")
    logger.info(f"Connection: {'SUCCESS' if connection_result else 'FAILED'}")
    logger.info(f"Auth: {'SUCCESS' if user_id else 'FAILED'}")
    logger.info(f"Credits: {'SUCCESS' if credits_result else 'FAILED'}")
    logger.info(f"Conversation: {'SUCCESS' if thread_id else 'FAILED'}")
    logger.info(f"Persistence: {'SUCCESS' if persistence_result else 'FAILED'}")


if __name__ == "__main__":
    asyncio.run(main())
