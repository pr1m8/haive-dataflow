
:py:mod:`dataflow.api.game_router_enhanced`
===========================================

.. py:module:: dataflow.api.game_router_enhanced

Enhanced Game Discovery and WebSocket API for Haive Games.

This module provides a comprehensive game discovery and management system using
haive-core's unified discovery infrastructure. It creates WebSocket endpoints
for real-time game state streaming and REST endpoints for game management.

Key Features:
    - Automatic discovery of game agents using haive-core
    - WebSocket-based real-time game state streaming
    - REST API for game creation and management
    - HTML client generation for browser-based gameplay
    - Support for multiple concurrent game sessions
    - Flexible agent initialization patterns

Architecture:
    - Uses HaiveComponentDiscovery for finding game agents
    - Creates dynamic routes for each discovered game
    - Maintains active game sessions in memory
    - Provides WebSocket connections for real-time updates

.. rubric:: Example

```python
# Run as standalone server
python game_router_enhanced.py

# Or integrate into existing FastAPI app
from haive.dataflow.api.game_router_enhanced import get_router

app = FastAPI()
games_router = get_router()
app.include_router(games_router, prefix="/games")
```

.. note::

   This implementation fixes the circular import issue and uses the
   unified discovery system from haive-core for consistency.


.. autolink-examples:: dataflow.api.game_router_enhanced
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.game_router_enhanced._discover_by_module_pattern
   dataflow.api.game_router_enhanced._get_game_client_javascript
   dataflow.api.game_router_enhanced._handle_ai_move
   dataflow.api.game_router_enhanced._handle_game_messages
   dataflow.api.game_router_enhanced._handle_game_websocket
   dataflow.api.game_router_enhanced._handle_get_state
   dataflow.api.game_router_enhanced._handle_make_move
   dataflow.api.game_router_enhanced._initialize_game_session
   dataflow.api.game_router_enhanced._instantiate_agent
   dataflow.api.game_router_enhanced._process_game_components
   dataflow.api.game_router_enhanced.create_game_instance
   dataflow.api.game_router_enhanced.create_game_router
   dataflow.api.game_router_enhanced.create_game_router_app
   dataflow.api.game_router_enhanced.discover_game_agents
   dataflow.api.game_router_enhanced.get_game_client_html
   dataflow.api.game_router_enhanced.get_game_instance
   dataflow.api.game_router_enhanced.get_index_html
   dataflow.api.game_router_enhanced.get_router
   dataflow.api.game_router_enhanced.main

.. py:function:: _discover_by_module_pattern(components: list[haive.dataflow.api.utils.haive_discovery.ComponentInfo]) -> None

   Discover games by module organization pattern.

   :param components: List of all discovered components.

   .. note::

      This catches games that might have non-standard naming
      but follow the module organization pattern.


   .. autolink-examples:: _discover_by_module_pattern
      :collapse:

.. py:function:: _get_game_client_javascript() -> str

   Get JavaScript code for the game client.

   :returns: JavaScript code for WebSocket communication and game UI.
   :rtype: str


   .. autolink-examples:: _get_game_client_javascript
      :collapse:

.. py:function:: _handle_ai_move(websocket: fastapi.WebSocket, agent: Any, game_type: str, game_id: str) -> None
   :async:


   Handle ai_move message.


   .. autolink-examples:: _handle_ai_move
      :collapse:

.. py:function:: _handle_game_messages(websocket: fastapi.WebSocket, agent: Any, game_type: str, game_id: str) -> None
   :async:


   Handle incoming WebSocket messages for a game.

   :param websocket: WebSocket connection.
   :param agent: Game agent instance.
   :param game_type: Type of game.
   :param game_id: Game identifier.


   .. autolink-examples:: _handle_game_messages
      :collapse:

.. py:function:: _handle_game_websocket(websocket: fastapi.WebSocket, game_type: str, game_id: str, agent_info: dict[str, Any]) -> None
   :async:


   Handle WebSocket connection for a game session.

   :param websocket: WebSocket connection object.
   :param game_type: Type of game.
   :param game_id: Unique game identifier.
   :param agent_info: Agent metadata.

   .. note::

      This function manages the entire WebSocket lifecycle including
      connection, message handling, and cleanup.


   .. autolink-examples:: _handle_game_websocket
      :collapse:

.. py:function:: _handle_get_state(websocket: fastapi.WebSocket, agent: Any, game_type: str, game_id: str) -> None
   :async:


   Handle get_state message.


   .. autolink-examples:: _handle_get_state
      :collapse:

.. py:function:: _handle_make_move(websocket: fastapi.WebSocket, agent: Any, game_type: str, game_id: str, data: dict[str, Any]) -> None
   :async:


   Handle make_move message.


   .. autolink-examples:: _handle_make_move
      :collapse:

.. py:function:: _initialize_game_session(websocket: fastapi.WebSocket, game_type: str, game_id: str, agent_info: dict[str, Any]) -> dict[str, Any] | None
   :async:


   Initialize a game session and send initial state.

   :param websocket: WebSocket connection.
   :param game_type: Type of game.
   :param game_id: Game identifier.
   :param agent_info: Agent metadata.

   :returns: Game instance or None if initialization fails.
   :rtype: Optional[Dict[str, Any]]


   .. autolink-examples:: _initialize_game_session
      :collapse:

.. py:function:: _instantiate_agent(agent_info: dict[str, Any], game_type: str, game_id: str) -> Any

   Instantiate a game agent with appropriate initialization.

   :param agent_info: Agent metadata and class information.
   :param game_type: Type of game.
   :param game_id: Unique game identifier.

   :returns: Instantiated agent object.
   :rtype: Any

   :raises RuntimeError: If all initialization patterns fail.


   .. autolink-examples:: _instantiate_agent
      :collapse:

.. py:function:: _process_game_components(components: list[haive.dataflow.api.utils.haive_discovery.ComponentInfo]) -> None

   Process discovered components to identify game agents.

   :param components: List of discovered components from the games package.

   .. note:: This function populates the global game_agents registry.


   .. autolink-examples:: _process_game_components
      :collapse:

.. py:function:: create_game_instance(game_type: str, game_id: str) -> dict[str, Any]

   Create or retrieve a game instance.

   :param game_type: Type of game to create (e.g., 'chess', 'checkers').
   :param game_id: Unique identifier for the game session.

   :returns:

             Game instance information including:
                 - agent: The instantiated game agent
                 - game_id: Unique game identifier
                 - game_type: Type of game
                 - created_at: Creation timestamp
                 - agent_info: Metadata about the agent
   :rtype: Dict[str, Any]

   :raises ValueError: If game_type is not recognized.
   :raises RuntimeError: If agent instantiation fails.

   .. note::

      Tries multiple initialization patterns to accommodate
      different agent implementations.


   .. autolink-examples:: create_game_instance
      :collapse:

.. py:function:: create_game_router(game_type: str) -> fastapi.APIRouter

   Create a router for a specific game type.

   :param game_type: Type of game to create routes for.

   :returns: Configured router with WebSocket and REST endpoints.
   :rtype: APIRouter

   :raises ValueError: If game_type is not recognized.

   .. note::

      Creates the following endpoints:
      - WebSocket: /ws/{game_type}/{game_id}
      - POST: /{game_type}/games - Create new game


   .. autolink-examples:: create_game_router
      :collapse:

.. py:function:: create_game_router_app() -> fastapi.FastAPI

   Create a standalone FastAPI app for game routes.

   :returns: Configured FastAPI application with game routes.
   :rtype: FastAPI

   .. note:: Includes CORS middleware for browser compatibility.


   .. autolink-examples:: create_game_router_app
      :collapse:

.. py:function:: discover_game_agents() -> None

   Discover game agents using the unified discovery system.

   This function scans the haive-games package for agent classes and
   their corresponding state classes, registering them for use.

   Discovery Process:
       1. Uses HaiveComponentDiscovery to find all components
       2. Filters for classes ending with 'Agent'
       3. Associates state classes with their agents
       4. Groups by game module for complete game discovery

   Side Effects:
       Updates the global game_agents registry with discovered games.

   .. note:: Skips base classes like 'BaseAgent', 'GenericAgent', etc.


   .. autolink-examples:: discover_game_agents
      :collapse:

.. py:function:: get_game_client_html(game_type: str) -> str

   Generate HTML for a specific game client.

   :param game_type: Type of game to generate client for.

   :returns: HTML content for the game client page.
   :rtype: str


   .. autolink-examples:: get_game_client_html
      :collapse:

.. py:function:: get_game_instance(game_type: str, game_id: str) -> dict[str, Any] | None

   Retrieve an existing game instance.

   :param game_type: Type of game.
   :param game_id: Unique game identifier.

   :returns: Game instance if found, None otherwise.
   :rtype: Optional[Dict[str, Any]]


   .. autolink-examples:: get_game_instance
      :collapse:

.. py:function:: get_index_html() -> str

   Generate HTML for the index page with links to all games.

   :returns: HTML content for the game index page.
   :rtype: str


   .. autolink-examples:: get_index_html
      :collapse:

.. py:function:: get_router() -> fastapi.APIRouter

   Get a router with all game routes configured.

   :returns: Main router containing all game-specific routers
             and the index page.
   :rtype: APIRouter

   .. note:: This function triggers game discovery if not already done.


   .. autolink-examples:: get_router
      :collapse:

.. py:function:: main()

   Run the API server as standalone application.


   .. autolink-examples:: main
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.game_router_enhanced
   :collapse:
   
.. autolink-skip:: next
