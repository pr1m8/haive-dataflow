# haive_dataflow/api/websockets/manager.py
import logging
from uuid import uuid4

from fastapi import WebSocket

from haive.dataflow.auth.supabase import SupabaseAuth
from haive.dataflow.config.environment import get_supabase_server_config

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: dict[str, dict[str, WebSocket]] = {}
        self.user_connections: dict[str, set[str]] = {}
        self.auth = SupabaseAuth(get_supabase_server_config())

    async def authenticate(self, websocket: WebSocket) -> str | None:
        """Authenticate a WebSocket connection.

        Args:
            websocket: The WebSocket connection

        Returns:
            User ID if authenticated, None otherwise
        """
        # Extract token from query params
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=1008, reason="Unauthorized")
            return None

        # Verify token
        user_id = self.auth.get_user_id(token)
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return None

        return user_id

    async def connect(self, websocket: WebSocket, thread_id: str) -> str | None:
        """Connect a client to a thread.

        Args:
            websocket: The WebSocket connection
            thread_id: Thread/conversation ID

        Returns:
            Connection ID if successful, None otherwise
        """
        # Authenticate
        user_id = await self.authenticate(websocket)
        if not user_id:
            return None

        # Accept connection
        await websocket.accept()

        # Generate connection ID
        connection_id = str(uuid4())

        # Store connection
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = {}
        self.active_connections[thread_id][connection_id] = websocket

        # Track user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Store metadata on websocket for later reference
        websocket.state.user_id = user_id
        websocket.state.thread_id = thread_id
        websocket.state.connection_id = connection_id

        # Send welcome message
        await websocket.send_json(
            {
                "type": "connected",
                "thread_id": thread_id,
                "connection_id": connection_id,
            }
        )

        return connection_id

    def disconnect(self, thread_id: str, connection_id: str) -> None:
        """Disconnect a client from a thread.

        Args:
            thread_id: Thread/conversation ID
            connection_id: Connection ID
        """
        # Remove connection
        if (
            thread_id in self.active_connections
            and connection_id in self.active_connections[thread_id]
        ):
            # Get user_id
            websocket = self.active_connections[thread_id][connection_id]
            user_id = getattr(websocket.state, "user_id", None)

            # Remove connection
            del self.active_connections[thread_id][connection_id]

            # Clean up if no more connections for thread
            if not self.active_connections[thread_id]:
                del self.active_connections[thread_id]

            # Remove from user connections
            if user_id and user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
