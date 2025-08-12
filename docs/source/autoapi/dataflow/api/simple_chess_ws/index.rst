
:py:mod:`dataflow.api.simple_chess_ws`
======================================

.. py:module:: dataflow.api.simple_chess_ws

Simple WebSocket server for streaming chess game state.


.. autolink-examples:: dataflow.api.simple_chess_ws
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.simple_chess_ws.get_empty_board
   dataflow.api.simple_chess_ws.get_game_state
   dataflow.api.simple_chess_ws.get_html
   dataflow.api.simple_chess_ws.main
   dataflow.api.simple_chess_ws.make_random_move
   dataflow.api.simple_chess_ws.websocket_endpoint

.. py:function:: get_empty_board()

   Create a new chess board in starting position.


   .. autolink-examples:: get_empty_board
      :collapse:

.. py:function:: get_game_state(game_id)

   Get the current game state.


   .. autolink-examples:: get_game_state
      :collapse:

.. py:function:: get_html()
   :async:


   Serve the HTML client.


   .. autolink-examples:: get_html
      :collapse:

.. py:function:: main()

   Run the WebSocket server.


   .. autolink-examples:: main
      :collapse:

.. py:function:: make_random_move(board)

   Make a random legal move.


   .. autolink-examples:: make_random_move
      :collapse:

.. py:function:: websocket_endpoint(websocket: fastapi.WebSocket, game_id: str)
   :async:


   WebSocket endpoint for chess games.


   .. autolink-examples:: websocket_endpoint
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.simple_chess_ws
   :collapse:
   
.. autolink-skip:: next
