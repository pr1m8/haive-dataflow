#!/usr/bin/env python3
"""Test WebSocket API with JWT authentication and check Supabase storage."""

import asyncio
import json
import os
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
    print("Testing WebSocket API with authentication...")

    # Create JWT token
    token = create_test_jwt()
    print("✓ Created JWT token")

    # Create unique thread ID
    thread_id = f"test-auth-{uuid4()}"
    print(f"Using thread ID: {thread_id}")

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
        print("\nConnecting to WebSocket with auth...")

        async with websockets.connect(
            "ws://localhost:8192/agents/ws", extra_headers=headers
        ) as websocket:
            print("✓ Connected to WebSocket")

            # Send message
            print("Sending message to agent...")
            await websocket.send(json.dumps(test_message))
            print("✓ Message sent")

            # Receive responses
            print("Waiting for response...")
            responses = []
            final_response = None

            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=45)
                    responses.append(response)
                    print(f"Received: {response[:100]}...")

                    # Try to parse as JSON
                    try:
                        data = json.loads(response)
                        if data.get("type") == "complete":
                            final_response = data.get("data", "")
                            print("✓ Received completion signal")
                            break
                        elif data.get("type") == "message":
                            # Extract the actual message content
                            content = data.get("data", {})
                            if isinstance(content, dict) and "content" in content:
                                final_response = content["content"]
                    except json.JSONDecodeError:
                        # Might be plain text response
                        final_response = response

            except asyncio.TimeoutError:
                print("Timeout waiting for response")
                if responses:
                    print(f"✓ Received {len(responses)} partial responses")
                    final_response = responses[-1] if responses else None
                else:
                    print("✗ No responses received")
                    return

    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")
        return

    print(f"\nFinal response: {final_response}")

    # Check Supabase database
    print("\n=== Checking Supabase Database ===")

    uri = "postgresql://postgres.zkssazqhwcetsnbiuqik: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@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

    try:
        conn = await psycopg.AsyncConnection.connect(uri)
        print("✓ Connected to Supabase")

        async with conn.cursor() as cursor:
            # Check public.threads table
            print(f"\nChecking for thread: {thread_id}")
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
                print("✓ Thread found in public.threads:")
                print(f"  Thread ID: {thread_row[0]}")
                print(f"  Name: {thread_row[1]}")
                print(f"  Metadata: {thread_row[2]}")
                print(f"  Created: {thread_row[3]}")
            else:
                print("✗ Thread not found in public.threads")

            # Check agent_state.checkpoints
            print(f"\nChecking for agent checkpoints...")
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
                print(f"✓ Found {checkpoint_stats[0]} checkpoints:")
                print(f"  First checkpoint: {checkpoint_stats[1]}")
                print(f"  Last checkpoint: {checkpoint_stats[2]}")
            else:
                print("✗ No checkpoints found in agent_state.checkpoints")

            # Check public.checkpoints (if exists)
            await cursor.execute(
                """
                SELECT COUNT(*) 
                FROM public.checkpoints 
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            public_checkpoints = (await cursor.fetchone())[0]
            print(f"\nPublic checkpoints: {public_checkpoints}")

            # Check if we can find any conversation data
            await cursor.execute(
                """
                SELECT COUNT(*) 
                FROM agent_state.conversations 
                WHERE thread_id = %s
            """,
                (thread_id,),
            )

            conversations = (await cursor.fetchone())[0]
            print(f"Conversations: {conversations}")

        await conn.close()

        # Summary
        data_found = thread_row or (checkpoint_stats and checkpoint_stats[0] > 0)

        if data_found:
            print("\n🎉 SUCCESS: Supabase persistence is working!")
            print("   - WebSocket authentication succeeded")
            print("   - Agent processed the message")
            print("   - Data was stored in Supabase database")
            if final_response:
                print(f"   - Agent responded: {final_response[:100]}...")
        else:
            print("\n⚠️  WebSocket worked but no data found in Supabase")
            print("   - Check if persistence is properly configured")

    except Exception as e:
        print(f"✗ Database check failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_websocket_with_auth())
