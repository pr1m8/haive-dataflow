
:py:mod:`dataflow.api.routes.agent_routes`
==========================================

.. py:module:: dataflow.api.routes.agent_routes

WebSocket and REST API endpoints for agent interactions.

This module provides WebSocket-based communication with Haive agents, enabling
real-time interactions, streaming responses, and persistent conversation state.
It also includes REST endpoints for agent management and configuration.

The WebSocket protocol supports different message types for user messages,
agent responses, status updates, and error handling. Connections are managed
per thread, allowing multiple concurrent agent sessions.

Key components:
- WebSocket connection manager for handling multiple clients
- Message types and formats for structured communication
- Authentication and authorization using Supabase
- Agent configuration and customization options
- Streaming response support for real-time feedback

Typical usage example:

    ```python
    # Client-side WebSocket example
    import websockets
    import json
    import asyncio

    async def connect_to_agent():
        uri = "ws://localhost:8000/api/ws/agent/chat?token=YOUR_AUTH_TOKEN"
        async with websockets.connect(uri) as websocket:
            # Send initial configuration
            await websocket.send(json.dumps({
                "type": "config",
                "content": {
                    "agent_name": "TextAnalyzer",
                    "provider": "openai",
                    "model": "gpt-4",
                    "stream": True
                }
            }))

            # Send a message to the agent
            await websocket.send(json.dumps({
                "type": "message",
                "content": "Analyze this text for sentiment"
            }))

            # Receive streaming responses
            while True:
                response = json.loads(await websocket.recv())
                if response["type"] == "response":
                    print(response["content"])
                elif response["type"] == "state_complete":
                    break

    asyncio.run(connect_to_agent())
    ```


.. autolink-examples:: dataflow.api.routes.agent_routes
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.agent_routes.AgentChatConfig
   dataflow.api.routes.agent_routes.ConnectionManager
   dataflow.api.routes.agent_routes.WSMessage
   dataflow.api.routes.agent_routes.WSMessageType


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for AgentChatConfig:

   .. graphviz::
      :align: center

      digraph inheritance_AgentChatConfig {
        node [shape=record];
        "AgentChatConfig" [label="AgentChatConfig"];
        "pydantic.BaseModel" -> "AgentChatConfig";
      }

.. autopydantic_model:: dataflow.api.routes.agent_routes.AgentChatConfig
   :members:
   :undoc-members:
   :show-inheritance:
   :model-show-field-summary:
   :model-show-config-summary:
   :model-show-validator-members:
   :model-show-validator-summary:
   :model-show-json:
   :field-list-validators:
   :field-show-constraints:





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for ConnectionManager:

   .. graphviz::
      :align: center

      digraph inheritance_ConnectionManager {
        node [shape=record];
        "ConnectionManager" [label="ConnectionManager"];
      }

.. autoclass:: dataflow.api.routes.agent_routes.ConnectionManager
   :members:
   :undoc-members:
   :show-inheritance:




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for WSMessage:

   .. graphviz::
      :align: center

      digraph inheritance_WSMessage {
        node [shape=record];
        "WSMessage" [label="WSMessage"];
        "pydantic.BaseModel" -> "WSMessage";
      }

.. autopydantic_model:: dataflow.api.routes.agent_routes.WSMessage
   :members:
   :undoc-members:
   :show-inheritance:
   :model-show-field-summary:
   :model-show-config-summary:
   :model-show-validator-members:
   :model-show-validator-summary:
   :model-show-json:
   :field-list-validators:
   :field-show-constraints:





.. toggle:: Show Inheritance Diagram

   Inheritance diagram for WSMessageType:

   .. graphviz::
      :align: center

      digraph inheritance_WSMessageType {
        node [shape=record];
        "WSMessageType" [label="WSMessageType"];
        "str" -> "WSMessageType";
        "enum.Enum" -> "WSMessageType";
      }

.. autoclass:: dataflow.api.routes.agent_routes.WSMessageType
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::

      **WSMessageType** is an Enum defined in ``dataflow.api.routes.agent_routes``.



Functions
---------

.. autoapisummary::

   dataflow.api.routes.agent_routes.configure_agent
   dataflow.api.routes.agent_routes.get_user_from_token
   dataflow.api.routes.agent_routes.load_agent_config
   dataflow.api.routes.agent_routes.reset_thread
   dataflow.api.routes.agent_routes.websocket_chat_endpoint

.. py:function:: configure_agent(config: haive.core.engine.base.agent_config.AgentConfig, chat_config: AgentChatConfig) -> haive.core.engine.base.agent_config.AgentConfig
   :async:


   Configure agent with LLM settings.


   .. autolink-examples:: configure_agent
      :collapse:

.. py:function:: get_user_from_token(token: str) -> str | None

   Validate JWT token and return user ID.


   .. autolink-examples:: get_user_from_token
      :collapse:

.. py:function:: load_agent_config(agent_name: str, user_id: str, thread_id: str) -> haive.core.engine.base.agent_config.AgentConfig | None
   :async:


   Load agent configuration from package.


   .. autolink-examples:: load_agent_config
      :collapse:

.. py:function:: reset_thread(thread_id: str, user_id: str = Depends(require_auth))
   :async:


   Reset/clear a chat thread.


   .. autolink-examples:: reset_thread
      :collapse:

.. py:function:: websocket_chat_endpoint(websocket: fastapi.WebSocket, agent_name: str, token: str = Query(..., description='JWT authentication token'), thread_id: str | None = Query(None, description='Existing thread ID for persistence'), config: str | None = Query(None, description='JSON encoded chat configuration'))
   :async:


   WebSocket endpoint for real-time chat with an agent.

   :param websocket: WebSocket connection
   :param agent_name: Name of the agent to chat with
   :param token: JWT authentication token
   :param thread_id: Optional thread ID for persistent chat
   :param config: Optional JSON-encoded chat configuration


   .. autolink-examples:: websocket_chat_endpoint
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.agent_routes
   :collapse:
   
.. autolink-skip:: next
