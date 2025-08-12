
:py:mod:`dataflow.llms.models`
==============================

.. py:module:: dataflow.llms.models

LLM Provider and Model Data Models.

This module defines Pydantic models for representing LLM providers, models,
and their capabilities within the Haive dataflow system. These models are
used for provider registration, capability tracking, and cost management.

Key Components:
    - Provider: LLM provider information and availability
    - Model: Comprehensive model specifications with capabilities
    - ModelCapabilities: Feature support matrix for each model
    - Pricing: Token-based pricing information
    - SearchPricing: Search-specific pricing tiers

.. rubric:: Example

Basic usage::

    from haive.dataflow.llms.models import Provider, Model, ModelCapabilities

    # Create a provider
    provider = Provider(
        name="OpenAI",
        is_available=True,
        created_at="2024-01-01T00:00:00Z",
        updated_at="2024-01-01T00:00:00Z"
    )

    # Define model capabilities
    capabilities = ModelCapabilities(
        supports_function_calling=True,
        supports_vision=True,
        supports_response_schema=True
    )

    # Create a model entry
    model = Model(
        model_id="gpt-4-vision-preview",
        provider="OpenAI",
        mode="chat",
        litellm_provider="openai",
        max_tokens=128000,
        max_input_tokens=120000,
        max_output_tokens=8000,
        capabilities=capabilities
    )

Advanced Usage:
    With pricing information::

        from haive.dataflow.llms.models import Pricing

        pricing = Pricing(
            input_cost_per_token=0.00001,
            output_cost_per_token=0.00003,
            cache_read_input_token_cost=0.000005
        )

        model = Model(
            model_id="claude-3-opus",
            provider="Anthropic",
            mode="chat",
            litellm_provider="anthropic",
            max_tokens=200000,
            max_input_tokens=180000,
            max_output_tokens=20000,
            pricing=pricing
        )

.. seealso::

   - haive.dataflow.registry: Model registration and discovery
   - haive.core.engine: Engine configuration using these models
   - haive.dataflow.providers: Provider implementation details

.. rubric:: Notes

- All token counts are measured in the model's native tokenization
- Pricing is in USD per token for standardized cost calculations
- Capabilities enable automatic feature detection and routing


.. autolink-examples:: dataflow.llms.models
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.llms.models.Model
   dataflow.llms.models.ModelCapabilities
   dataflow.llms.models.Pricing
   dataflow.llms.models.Provider
   dataflow.llms.models.SearchPricing


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for Model:

   .. graphviz::
      :align: center

      digraph inheritance_Model {
        node [shape=record];
        "Model" [label="Model"];
        "pydantic.BaseModel" -> "Model";
      }

.. autopydantic_model:: dataflow.llms.models.Model
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

   Inheritance diagram for ModelCapabilities:

   .. graphviz::
      :align: center

      digraph inheritance_ModelCapabilities {
        node [shape=record];
        "ModelCapabilities" [label="ModelCapabilities"];
        "pydantic.BaseModel" -> "ModelCapabilities";
      }

.. autopydantic_model:: dataflow.llms.models.ModelCapabilities
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

   Inheritance diagram for Pricing:

   .. graphviz::
      :align: center

      digraph inheritance_Pricing {
        node [shape=record];
        "Pricing" [label="Pricing"];
        "pydantic.BaseModel" -> "Pricing";
      }

.. autopydantic_model:: dataflow.llms.models.Pricing
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

   Inheritance diagram for Provider:

   .. graphviz::
      :align: center

      digraph inheritance_Provider {
        node [shape=record];
        "Provider" [label="Provider"];
        "pydantic.BaseModel" -> "Provider";
      }

.. autopydantic_model:: dataflow.llms.models.Provider
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

   Inheritance diagram for SearchPricing:

   .. graphviz::
      :align: center

      digraph inheritance_SearchPricing {
        node [shape=record];
        "SearchPricing" [label="SearchPricing"];
        "pydantic.BaseModel" -> "SearchPricing";
      }

.. autopydantic_model:: dataflow.llms.models.SearchPricing
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





.. rubric:: Related Links

.. autolink-examples:: dataflow.llms.models
   :collapse:
   
.. autolink-skip:: next
