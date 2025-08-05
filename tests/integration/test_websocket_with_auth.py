#!/usr/bin/env python3
"""Test WebSocket API with JWT authentication and check Supabase storage."""

import asyncio
import json
from datetime import datetime, timedelta
from uuid import uuid4

import jwt
import psycopg
import websockets


def create_test_jwt():
    """Create a test JWT token for authentication."""
    # Use the JWT secret from .env
    jwt_secret = "J89XqGf7hDkKejOK1n02TKVT78TtncD3gP0TH68N4AV1H87viAt9EhQxVp0mfUxkBNHowVCng2okkmPHYZpiKA=="

    # Create payload
    payload = {
        "sub": "test-user-123",  # User ID
        "aud": "authenticated",
        "role": "authenticated",
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    # Generate token
    token = jwt.encode(payload, jwt_secret, algorithm="HS256")
    return token


async def test_websocket_with_auth():
    """Test WebSocket with authentication and verify Supabase storage."""
    # Create JWT token
    token = create_test_jwt()

    # Create unique thread ID
    thread_id = f"test-auth-{uuid4()}"

    # Test message
    test_message = {
        "message": "Hello! Can you remember that my favorite hobby is photography?",
        "agent_id": "simple",
        "user_id": "test-user-123",
        "thread_id": thread_id,
        "stream_mode": "messages",
    }

    try:
        # Connect to WebSocket with authorization header
        headers = {"Authorization": f"Bearer {token}"}

        async with websockets.connect(
            "ws://localhost:8192/agents/ws", extra_headers=headers
        ) as websocket:
            # Send message
            await websocket.send(json.dumps(test_message))

            # Receive responses
            responses = []
            final_response = None

            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=45)
                    responses.append(response)

                    # Try to parse as JSON
                    try:
                        data = json.loads(response)
                        if data.get("type") == "complete":
                            final_response = data.get("data", "")
                            break
                        if data.get("type") == "message":
                            # Extract the actual message content
                            content = data.get("data", {})
                            if isinstance(content, dict) and "content" in content:
                                final_response = content["content"]
                    except json.JSONDecodeError:
                        # Might be plain text response
                        final_response = response

            except TimeoutError:
                if responses:
                    final_response = responses[-1] if responses else None
                else:
                    return

    except Exception:
        return

    # Check Supabase database

    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        conn = await psycopg.AsyncConnection.connect(uri)

        async with conn.cursor() as cursor:
            # Check public.threads table
            await cursor.execute(
                """
                SELECT thread_id, name, metadata, created_at
                FROM public.threads
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            thread_row = await cursor.fetchone()
            if thread_row:
                pass
            else:
                pass

            # Check agent_state.checkpoints
            await cursor.execute(
                """
                SELECT COUNT(*), MIN(created_at), MAX(created_at)
                FROM agent_state.checkpoints
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            checkpoint_stats = await cursor.fetchone()
            if checkpoint_stats and checkpoint_stats[0] > 0:
                pass
            else:
                pass

            # Check public.checkpoints (if exists)
            await cursor.execute(
                """
                SELECT COUNT(*)
                FROM public.checkpoints
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            (await cursor.fetchone())[0]

            # Check if we can find any conversation data
            await cursor.execute(
                """
                SELECT COUNT(*)
                FROM agent_state.conversations
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            (await cursor.fetchone())[0]

        await conn.close()

        # Summary
        data_found = thread_row or (checkpoint_stats and checkpoint_stats[0] > 0)

        if data_found:
            if final_response:
                pass
        else:
            pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_websocket_with_auth())
