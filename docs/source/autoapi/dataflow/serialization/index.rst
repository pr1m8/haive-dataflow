
:py:mod:`dataflow.serialization`
================================

.. py:module:: dataflow.serialization

Serialization utilities for the Haive Registry System.

This module provides tools for serializing and deserializing complex
Python objects for storage in the registry database.


.. autolink-examples:: dataflow.serialization
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.serialization.SerializationRegistry


Module Contents
---------------




.. toggle:: Show Inheritance Diagram

   Inheritance diagram for SerializationRegistry:

   .. graphviz::
      :align: center

      digraph inheritance_SerializationRegistry {
        node [shape=record];
        "SerializationRegistry" [label="SerializationRegistry"];
      }

.. autoclass:: dataflow.serialization.SerializationRegistry
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.serialization._deserialize_pydantic_model
   dataflow.serialization._serialize_pydantic_field
   dataflow.serialization._serialize_pydantic_model
   dataflow.serialization._serialize_type_hints
   dataflow.serialization.deserialize_object
   dataflow.serialization.serialize_object

.. py:function:: _deserialize_pydantic_model(data: dict[str, Any]) -> type[pydantic.BaseModel] | None

   Deserialize a Pydantic model class.

   Note: This creates a simple representation of the model, not the actual class.


   .. autolink-examples:: _deserialize_pydantic_model
      :collapse:

.. py:function:: _serialize_pydantic_field(field)

   Serialize a Pydantic field.


   .. autolink-examples:: _serialize_pydantic_field
      :collapse:

.. py:function:: _serialize_pydantic_model(model: type[pydantic.BaseModel]) -> dict[str, Any]

   Serialize a Pydantic model class.


   .. autolink-examples:: _serialize_pydantic_model
      :collapse:

.. py:function:: _serialize_type_hints(hints: dict[str, Any]) -> dict[str, str]

   Serialize type hints.


   .. autolink-examples:: _serialize_type_hints
      :collapse:

.. py:function:: deserialize_object(data: dict[str, Any]) -> Any

   Deserialize an object from stored data.

   :param data: Serialized representation

   :returns: Deserialized object


   .. autolink-examples:: deserialize_object
      :collapse:

.. py:function:: serialize_object(obj: Any) -> dict[str, Any]

   Serialize an object to a format suitable for storage.

   :param obj: Object to serialize

   :returns: Serialized representation as a JSON-compatible dict


   .. autolink-examples:: serialize_object
      :collapse:



.. rubric:: Related Links

.. autolink-examples:: dataflow.serialization
   :collapse:
   
.. autolink-skip:: next
