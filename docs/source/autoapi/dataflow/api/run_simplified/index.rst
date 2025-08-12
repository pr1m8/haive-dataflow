
:py:mod:`dataflow.api.run_simplified`
=====================================

.. py:module:: dataflow.api.run_simplified

Simplified demo to launch a WebSocket server for chess games.

This is a minimal implementation that focuses on getting the WebSocket
functionality working without the full API infrastructure.


.. autolink-examples:: dataflow.api.run_simplified
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.run_simplified.get_client
   dataflow.api.run_simplified.get_current_player
   dataflow.api.run_simplified.get_empty_board
   dataflow.api.run_simplified.get_game_state
   dataflow.api.run_simplified.get_game_status
   dataflow.api.run_simplified.main
   dataflow.api.run_simplified.make_ai_move
   dataflow.api.run_simplified.make_move
   dataflow.api.run_simplified.move_is_valid
   dataflow.api.run_simplified.websocket_endpoint

.. py:function:: get_client()
   :async:


   Serve the chess client HTML.


   .. autolink-examples:: get_client
      :collapse:

.. py:function:: get_current_player(board)

   Get the current player.


   .. autolink-examples:: get_current_player
      :collapse:

.. py:function:: get_empty_board()

   Create an empty chess board in starting position.


   .. autolink-examples:: get_empty_board
      :collapse:

.. py:function:: get_game_state(game_id)

   Get the full game state.


   .. autolink-examples:: get_game_state
      :collapse:

.. py:function:: get_game_status(board)

   Get the current game status.


   .. autolink-examples:: get_game_status
      :collapse:

.. py:function:: main()

   Run the WebSocket server.


   .. autolink-examples:: main
      :collapse:

.. py:function:: make_ai_move(websocket: fastapi.WebSocket, game_id: str)
   :async:


   Make a simple AI move.


   .. autolink-examples:: make_ai_move
      :collapse:

.. py:function:: make_move(board, move_uci)

   Make a move on the board.


   .. autolink-examples:: make_move
      :collapse:

.. py:function:: move_is_valid(board, move_uci)

   Check if a move is valid.


   .. autolink-examples:: move_is_valid
      :collapse:

.. py:function:: websocket_endpoint(websocket: fastapi.WebSocket, game_id: str)
   :async:


   WebSocket endpoint for chess games.


   .. autolink-examples:: websocket_endpoint
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.run_simplified
   :collapse:
   
.. autolink-skip:: next
