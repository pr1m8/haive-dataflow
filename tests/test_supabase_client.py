# test_supabase_direct.py
import asyncio
import json
import logging
import os

import jwt
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("direct_test")


async def test_supabase_direct():
    """Test Supabase connection directly."""
    from supabase import create_client

    # Get credentials
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    # Connect
    client = create_client(url, anon_key)

    # Test query
    response = await client.from_("threads").select("*").limit(1).execute()

    # Log result
    logger.info(f"Status: {response.status_code}")
    logger.info(f"Data: {json.dumps(response.data)}")

    return True


async def test_jwt_direct():
    """Test JWT verification directly."""
    token = os.getenv("TEST_SUPABASE_TOKEN")
    secret = os.getenv("SUPABASE_JWT_SECRET")

    try:
        # Decode without verification first to see payload
        decoded_no_verify = jwt.decode(token, options={"verify_signature": False})
        logger.info(f"Token payload (no verify): {json.dumps(decoded_no_verify)}")

        # Now try with verification
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        logger.info(f"Token payload (verified): {json.dumps(decoded)}")

        return True
    except Exception as e:
        logger.exception(f"JWT error: {e}")
        return False


async def main():
    await test_supabase_direct()
    await test_jwt_direct()


if __name__ == "__main__":
    asyncio.run(main())
