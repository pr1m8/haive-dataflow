
:py:mod:`dataflow.base`
=======================

.. py:module:: dataflow.base


Classes
-------

.. autoapisummary::

   dataflow.base.LLMConfigRequest
   dataflow.base.LLMGenerationResponse
   dataflow.base.ToolConfig


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

.. autopydantic_model:: dataflow.base.LLMConfigRequest
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

.. autopydantic_model:: dataflow.base.LLMGenerationResponse
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

.. autopydantic_model:: dataflow.base.ToolConfig
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

   dataflow.base.generate_response
   dataflow.base.get_env_api_key
   dataflow.base.root

.. py:function:: generate_response(request: LLMConfigRequest, query: str = Query(..., description='The input query or message to generate a response for'))
   :async:


   Generate a response using dynamically configured LLM.

   :param request: LLM configuration details
   :param query: User's input query


   .. autolink-examples:: generate_response
      :collapse:

.. py:function:: get_env_api_key(provider: haive.dataflow.models.llm.provider_types.LLMProvider) -> str | None

   Retrieve API key from environment variables based on provider.


   .. autolink-examples:: get_env_api_key
      :collapse:

.. py:function:: root()
   :async:




.. rubric:: Related Links

.. autolink-examples:: dataflow.base
   :collapse:
   
.. autolink-skip:: next
