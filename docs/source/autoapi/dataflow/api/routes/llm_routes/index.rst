
:py:mod:`dataflow.api.routes.llm_routes`
========================================

.. py:module:: dataflow.api.routes.llm_routes

LLM model API routes and generation endpoints.

This module provides FastAPI routes for interacting with various LLM providers
and models. It supports generating text completions, chat completions, and
streaming responses from models like OpenAI GPT, Anthropic Claude, Google Gemini,
and others.

The routes handle provider-specific configurations, authentication, and proper
error handling. They serve as the interface between clients and the underlying
LLM functionality provided by the Haive core modules.

Key features:
- Multi-provider support (OpenAI, Azure, Anthropic, Gemini, etc.)
- Text and chat completion endpoints
- Streaming response support
- Model information endpoints
- Authentication and rate limiting

Typical usage example:

    ```python
    # Client-side code to generate text
    import requests

    response = requests.post(
        "http://localhost:8000/api/llm/generate",
        json={
            "provider": "openai",
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Tell me about AI."}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        },
        headers={"Authorization": "Bearer YOUR_TOKEN"}
    )

    generated_text = response.json()["generated_text"]
    ```


.. autolink-examples:: dataflow.api.routes.llm_routes
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.api.routes.llm_routes.LLMConfigRequest
   dataflow.api.routes.llm_routes.LLMGenerationResponse
   dataflow.api.routes.llm_routes.ToolConfig


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for LLMConfigRequest:

   .. graphviz::
      :align: center

      digraph inheritance_LLMConfigRequest {
        node [shape=record];
        "LLMConfigRequest" [label="LLMConfigRequest"];
        "pydantic.BaseModel" -> "LLMConfigRequest";
      }

.. autopydantic_model:: dataflow.api.routes.llm_routes.LLMConfigRequest
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

   Inheritance diagram for LLMGenerationResponse:

   .. graphviz::
      :align: center

      digraph inheritance_LLMGenerationResponse {
        node [shape=record];
        "LLMGenerationResponse" [label="LLMGenerationResponse"];
        "pydantic.BaseModel" -> "LLMGenerationResponse";
      }

.. autopydantic_model:: dataflow.api.routes.llm_routes.LLMGenerationResponse
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

   Inheritance diagram for ToolConfig:

   .. graphviz::
      :align: center

      digraph inheritance_ToolConfig {
        node [shape=record];
        "ToolConfig" [label="ToolConfig"];
        "pydantic.BaseModel" -> "ToolConfig";
      }

.. autopydantic_model:: dataflow.api.routes.llm_routes.ToolConfig
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



Functions
---------

.. autoapisummary::

   dataflow.api.routes.llm_routes.batch_generate
   dataflow.api.routes.llm_routes.generate_response
   dataflow.api.routes.llm_routes.get_env_api_key

.. py:function:: batch_generate(request: fastapi.Request, user_id: str = Depends(require_auth))
   :async:


   Generate responses from multiple LLM configurations in parallel.

   :param request: The HTTP request containing the configurations
   :param user_id: Authenticated user ID


   .. autolink-examples:: batch_generate
      :collapse:

.. py:function:: generate_response(request: LLMConfigRequest, query: str = Query(..., description='The input query or message to generate a response for'), user_id: str = Depends(require_auth))
   :async:


   Generate a response using dynamically configured LLM.

   :param request: LLM configuration details
   :param query: User's input query
   :param user_id: Authenticated user ID


   .. autolink-examples:: generate_response
      :collapse:

.. py:function:: get_env_api_key(provider: haive.dataflow.api.routes.models.llm.provider_types.LLMProvider) -> str | None

   Retrieve API key from environment variables based on provider.


   .. autolink-examples:: get_env_api_key
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.api.routes.llm_routes
   :collapse:
   
.. autolink-skip:: next
