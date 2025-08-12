
:py:mod:`dataflow.registry.serialization`
=========================================

.. py:module:: dataflow.registry.serialization

Serialization utilities for the Haive Registry System.

This module provides tools for serializing and deserializing complex Python objects
for storage in the registry database. It handles the conversion of objects that
aren't natively JSON-serializable, such as classes, functions, and custom types.

The serialization system uses a registry of custom serializers and deserializers
for specific types, allowing for extensible handling of different object types.
This enables the storage and retrieval of complex objects while preserving their
structure and relationships.

Classes:
    SerializationRegistry: Registry for managing custom serializers and deserializers

Functions:
    serialize_object: Convert a complex object to a JSON-serializable format
    deserialize_object: Restore an object from its serialized representation

.. rubric:: Example

Basic serialization and deserialization:

>>> from haive.dataflow.registry.serialization import serialize_object, deserialize_object
>>>
>>> # Create a complex object
>>> class CustomObject:
...     def __init__(self, name, value):
...         self.name = name
...         self.value = value
>>>
>>> obj = CustomObject("test", 42)
>>>
>>> # Serialize it
>>> serialized = serialize_object(obj)
>>> print(f"Serialized: {serialized}")
>>>
>>> # Deserialize it
>>> restored = deserialize_object(serialized)
>>> print(f"Restored: {restored.name}, {restored.value}")

.. rubric:: Example

Registering custom serializers:

>>> from haive.dataflow.registry.serialization import SerializationRegistry
>>>
>>> # Register serializer and deserializer for a custom type
>>> SerializationRegistry.register(
...     type_name="my_module.CustomType",
...     serializer=lambda obj: {"data": obj.to_dict()},
...     deserializer=lambda data: CustomType.from_dict(data["data"])
... )


.. autolink-examples:: dataflow.registry.serialization
   :collapse:

Classes
-------

.. autoapisummary::

   dataflow.registry.serialization.SerializationRegistry


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

.. autoclass:: dataflow.registry.serialization.SerializationRegistry
   :members:
   :undoc-members:
   :show-inheritance:


Functions
---------

.. autoapisummary::

   dataflow.registry.serialization._deserialize_pydantic_model
   dataflow.registry.serialization._serialize_pydantic_field
   dataflow.registry.serialization._serialize_pydantic_model
   dataflow.registry.serialization._serialize_type_hints
   dataflow.registry.serialization.deserialize_object
   dataflow.registry.serialization.serialize_object

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

.. autolink-examples:: dataflow.registry.serialization
   :collapse:
   
.. autolink-skip:: next
