
:py:mod:`dataflow.api.app`
==========================

.. py:module:: dataflow.api.app

Haive API Application Module.

This module defines and configures the FastAPI application for the Haive framework.
It sets up middleware, routes, and the core API functionality.

The API provides RESTful and WebSocket endpoints for interacting with the Haive
registry, agents, conversations, and LLM models. It includes authentication,
request logging, and rate limiting middleware.

It also provides WebSocket endpoints for streaming game agent states, with
dynamic discovery of available games from the haive-games package.

Typical usage example:

    ```python
    from haive.dataflow.api.app import app
    import uvicorn

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    ```


.. autolink-examples:: dataflow.api.app
   :collapse:


Functions
---------

.. autoapisummary::

   dataflow.api.app.create_app
   dataflow.api.app.validation_exception_handler

.. py:function:: create_app() -> fastapi.FastAPI

   Create and configure the FastAPI application.

   This function creates a new FastAPI application instance, configures middleware
   for CORS, authentication, logging, and rate limiting, and registers the API
   routes for agents, conversations, LLM models, and game agents.

   The application configuration is loaded from settings, allowing for
   environment-specific customization.

   :returns: A configured FastAPI application instance ready to serve requests.
   :rtype: FastAPI

   .. rubric:: Example

   >>> app = create_app()
   >>> # Run the app with Uvicorn
   >>> import uvicorn
   >>> uvicorn.run(app, host="0.0.0.0", port=8000)


   .. autolink-examples:: create_app
      :collapse:

.. py:function:: validation_exception_handler(request, exc)
   :async:




.. rubric:: Related Links

.. autolink-examples:: dataflow.api.app
   :collapse:
   
.. autolink-skip:: next
