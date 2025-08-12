
:py:mod:`dataflow.config.settings`
==================================

.. py:module:: dataflow.config.settings

Application settings configuration for the Haive framework.

This module defines Pydantic models for application settings, providing
a type-safe and validated configuration system. Settings are automatically
loaded from environment variables with sensible defaults.

The settings hierarchy includes:
- AppSettings: Top-level application settings
- APISettings: API-specific settings
- AgentSettings: Agent-specific settings

Settings can be accessed using the get_settings() function, which returns
a singleton instance of the AppSettings class.

Typical usage example:

    ```python
    from haive.dataflow.config.settings import get_settings

    settings = get_settings()

    # Access settings properties
    api_prefix = settings.api.prefix
    is_production = settings.is_production
    agent_timeout = settings.agent.default_timeout

    # Use in application logic
    if settings.is_development:
        print(f"Running in development mode with debug={settings.api.debug}")
    ```


.. autolink-examples:: dataflow.config.settings
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.config.settings.AgentSettings
   dataflow.config.settings.APISettings
   dataflow.config.settings.AppSettings


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for APISettings:

   .. graphviz::
      :align: center

      digraph inheritance_APISettings {
        node [shape=record];
        "APISettings" [label="APISettings"];
        "pydantic.BaseModel" -> "APISettings";
      }

.. autopydantic_model:: dataflow.config.settings.APISettings
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

   Inheritance diagram for AgentSettings:

   .. graphviz::
      :align: center

      digraph inheritance_AgentSettings {
        node [shape=record];
        "AgentSettings" [label="AgentSettings"];
        "pydantic.BaseModel" -> "AgentSettings";
      }

.. autopydantic_model:: dataflow.config.settings.AgentSettings
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

   Inheritance diagram for AppSettings:

   .. graphviz::
      :align: center

      digraph inheritance_AppSettings {
        node [shape=record];
        "AppSettings" [label="AppSettings"];
        "pydantic.BaseModel" -> "AppSettings";
      }

.. autopydantic_model:: dataflow.config.settings.AppSettings
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

   dataflow.config.settings.get_settings

.. py:function:: get_settings() -> AppSettings

   Get application settings.


   .. autolink-examples:: get_settings
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.config.settings
   :collapse:
   
.. autolink-skip:: next
