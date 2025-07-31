"""Serialization utilities for the Haive Registry System.

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

Example:
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

Example:
    Registering custom serializers:

    >>> from haive.dataflow.registry.serialization import SerializationRegistry
    >>>
    >>> # Register serializer and deserializer for a custom type
    >>> SerializationRegistry.register(
    ...     type_name="my_module.CustomType",
    ...     serializer=lambda obj: {"data": obj.to_dict()},
    ...     deserializer=lambda data: CustomType.from_dict(data["data"])
    ... )
"""

import logging
import types
from collections.abc import Callable
from enum import Enum
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class SerializationRegistry:
    """Registry for serializers and deserializers.

    This registry allows the system to handle complex Python objects by registering
    custom serializers and deserializers for specific types. It maintains mappings
    from type names to serializer and deserializer functions, enabling consistent
    conversion of complex objects to and from serializable formats.

    The registry is used by the serialize_object and deserialize_object functions
    to handle types that aren't natively JSON-serializable.

    Attributes:
        _serializers (dict): Mapping from type names to serializer functions
        _deserializers (dict): Mapping from type names to deserializer functions

    Example:
        >>> from haive.dataflow.registry.serialization import SerializationRegistry
        >>>
        >>> # Define a custom type
        >>> class CustomType:
        ...     def __init__(self, name, value):
        ...         self.name = name
        ...         self.value = value
        ...
        ...     def to_dict(self):
        ...         return {"name": self.name, "value": self.value}
        ...
        ...     @classmethod
        ...     def from_dict(cls, data):
        ...         return cls(data["name"], data["value"])
        >>>
        >>> # Register serializer and deserializer
        >>> SerializationRegistry.register(
        ...     type_name="__main__.CustomType",
        ...     serializer=lambda obj: {"data": obj.to_dict()},
        ...     deserializer=lambda data: CustomType.from_dict(data["data"])
        ... )
    """

    _serializers = {}
    _deserializers = {}

    @classmethod
    def register(
        cls,
        type_name: str,
        serializer: Callable,
        deserializer: Callable | None = None,
    ):
        """Register serializer and deserializer for a type.

        Args:
            type_name: Fully qualified type name
            serializer: Function to serialize objects of this type
            deserializer: Function to deserialize objects of this type
        """
        cls._serializers[type_name] = serializer
        if deserializer:
            cls._deserializers[type_name] = deserializer

    @classmethod
    def can_serialize(cls, obj: Any) -> bool:
        """Check if the object can be serialized with a registered serializer.

        Args:
            obj: Object to check

        Returns:
            True if a serializer is available, False otherwise
        """
        obj_type = type(obj)
        for type_name in cls._serializers:
            try:
                # Try to resolve the type name to an actual type
                resolved_type = cls._resolve_type(type_name)
                if resolved_type and isinstance(obj, resolved_type):
                    return True
            except (NameError, AttributeError):
                # Failed to resolve, try direct type name comparison
                if obj_type.__module__ + "." + obj_type.__name__ == type_name:
                    return True
        return False

    @classmethod
    def _resolve_type(cls, type_name: str) -> type | None:
        """Resolve a type name to an actual type.

        Args:
            type_name: Fully qualified type name

        Returns:
            Resolved type or None if resolution fails
        """
        try:
            # Split module and class
            if "." in type_name:
                module_name, class_name = type_name.rsplit(".", 1)
                module = __import__(module_name, fromlist=[class_name])
                return getattr(module, class_name)
            # Built-in type
            return globals().get(type_name) or __builtins__.get(type_name)
        except (ImportError, AttributeError) as e:
            logger.debug(f"Failed to resolve type {type_name}: {e}")
            return None

    @classmethod
    def serialize(cls, obj: Any) -> Any:
        """Serialize an object using registered serializers.

        Args:
            obj: Object to serialize

        Returns:
            Serialized representation of the object
        """
        # Handle None
        if obj is None:
            return None

        # Get the object type
        obj_type = type(obj)
        obj_type_name = obj_type.__module__ + "." + obj_type.__name__

        # Try direct serializers first
        for type_name, serializer in cls._serializers.items():
            try:
                resolved_type = cls._resolve_type(type_name)
                if resolved_type and isinstance(obj, resolved_type):
                    return {"__type__": type_name, "data": serializer(obj)}
            except Exception as e:
                logger.warning(f"Error in serializer for {type_name}: {e}")

        # Handle built-in types
        if isinstance(obj, str | int | float | bool | type(None)):
            return obj

        # Handle dictionaries
        if isinstance(obj, dict):
            return {key: cls.serialize(value) for key, value in obj.items()}

        # Handle lists and tuples
        if isinstance(obj, list | tuple):
            serialized = [cls.serialize(item) for item in obj]
            if isinstance(obj, tuple):
                return {"__type__": "tuple", "data": serialized}
            return serialized

        # Handle sets
        if isinstance(obj, set):
            return {"__type__": "set", "data": [cls.serialize(item) for item in obj]}

        # Handle Enums
        if isinstance(obj, Enum):
            return {"__type__": obj_type_name, "data": obj.name}

        # Handle Pydantic models
        if isinstance(obj, BaseModel):
            data = obj.model_dump() if hasattr(obj, "model_dump") else obj.dict()
            return {"__type__": obj_type_name, "data": cls.serialize(data)}

        # Handle functions and methods
        if isinstance(obj, types.FunctionType | types.MethodType):
            return {
                "__type__": "function",
                "data": {
                    "module": obj.__module__,
                    "name": obj.__name__,
                    "is_method": isinstance(obj, types.MethodType),
                },
            }

        # Handle classes
        if isinstance(obj, type):
            return {
                "__type__": "class",
                "data": {"module": obj.__module__, "name": obj.__name__},
            }

        # Handle objects with __dict__
        if hasattr(obj, "__dict__"):
            return {"__type__": obj_type_name, "data": cls.serialize(obj.__dict__)}

        # Last resort - try to convert to string
        try:
            return {"__type__": "string_representation", "data": str(obj)}
        except Exception:
            logger.warning(f"Could not serialize object of type {obj_type_name}")
            return None

    @classmethod
    def deserialize(cls, data: Any) -> Any:
        """Deserialize an object using registered deserializers.

        Args:
            data: Serialized data

        Returns:
            Deserialized object
        """
        # Handle None and primitive types
        if data is None or isinstance(data, str | int | float | bool):
            return data

        # Handle typed objects
        if isinstance(data, dict) and "__type__" in data:
            type_name = data["__type__"]
            type_data = data["data"]

            # Use registered deserializer if available
            if type_name in cls._deserializers:
                try:
                    return cls._deserializers[type_name](type_data)
                except Exception as e:
                    logger.warning(f"Error in deserializer for {type_name}: {e}")

            # Handle tuples
            if type_name == "tuple":
                return tuple(cls.deserialize(item) for item in type_data)

            # Handle sets
            if type_name == "set":
                return {cls.deserialize(item) for item in type_data}

            # Handle functions
            if type_name == "function":
                try:
                    module = __import__(
                        type_data["module"], fromlist=[type_data["name"]]
                    )
                    return getattr(module, type_data["name"])
                except Exception as e:
                    logger.warning(
                        f"Error deserializing function {
                            type_data['module']}.{
                            type_data['name']}: {e}")
                    return None

            # Handle classes
            if type_name == "class":
                try:
                    module = __import__(
                        type_data["module"], fromlist=[type_data["name"]]
                    )
                    return getattr(module, type_data["name"])
                except Exception as e:
                    logger.warning(
                        f"Error deserializing class {
                            type_data['module']}.{
                            type_data['name']}: {e}")
                    return None

            # Handle string representations
            if type_name == "string_representation":
                return type_data

            # Try to deserialize enums
            try:
                enum_type = cls._resolve_type(type_name)
                if enum_type and issubclass(enum_type, Enum):
                    return getattr(enum_type, type_data)
            except Exception:
                pass

            # Try to deserialize Pydantic models
            try:
                model_type = cls._resolve_type(type_name)
                if model_type and issubclass(model_type, BaseModel):
                    deserialized_data = cls.deserialize(type_data)
                    return model_type(**deserialized_data)
            except Exception:
                pass

            # For unknown types, return the data as is
            return type_data

        # Handle dictionaries
        if isinstance(data, dict):
            return {key: cls.deserialize(value) for key, value in data.items()}

        # Handle lists
        if isinstance(data, list):
            return [cls.deserialize(item) for item in data]

        # Default case
        return data


# Register serializers for common types


def _serialize_type_hints(hints: dict[str, Any]) -> dict[str, str]:
    """Serialize type hints."""
    result = {}
    for name, hint in hints.items():
        try:
            # Convert type hint to string representation
            if isinstance(hint, type):
                result[name] = f"{hint.__module__}.{hint.__name__}"
            else:
                result[name] = str(hint)
        except Exception:
            result[name] = "Any"
    return result


def _serialize_pydantic_field(field):
    """Serialize a Pydantic field."""
    data = {
        "name": field.name,
        "required": field.required,
        "default": SerializationRegistry.serialize(field.default),
    }

    # Add type information if available
    if hasattr(field, "annotation"):
        data["type"] = str(field.annotation)
    elif hasattr(field, "type_"):
        data["type"] = str(field.type_)

    # Add other field properties
    for prop in ["description", "title", "min_length", "max_length", "ge", "le"]:
        if hasattr(field, prop) and getattr(field, prop) is not None:
            data[prop] = getattr(field, prop)

    return data


def _serialize_pydantic_model(model: type[BaseModel]) -> dict[str, Any]:
    """Serialize a Pydantic model class."""
    data = {
        "name": model.__name__,
        "module": model.__module__,
        "fields": [],
        "validators": [],
    }

    # Handle different Pydantic versions
    if hasattr(model, "model_fields"):  # Pydantic v2
        for name, field in model.model_fields.items():
            field_data = _serialize_pydantic_field(field)
            field_data["name"] = name
            data["fields"].append(field_data)
    elif hasattr(model, "__fields__"):  # Pydantic v1
        for name, field in model.__fields__.items():
            data["fields"].append(_serialize_pydantic_field(field))

    # Get validators (for Pydantic v1)
    if hasattr(model, "__validators__"):
        data["validators"] = list(model.__validators__.keys())

    # Get config
    if hasattr(model, "Config"):
        config_dict = {}
        for key in dir(model.Config):
            if not key.startswith("__"):
                config_dict[key] = getattr(model.Config, key)
        data["config"] = config_dict

    return data


def _deserialize_pydantic_model(data: dict[str, Any]) -> type[BaseModel] | None:
    """Deserialize a Pydantic model class.

    Note: This creates a simple representation of the model, not the actual class.
    """
    try:
        # Try to import the actual model
        module_name = data["module"]
        class_name = data["name"]

        module = __import__(module_name, fromlist=[class_name])
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        logger.debug(f"Could not import model {data['module']}.{data['name']}")

        # Return a dict representation as fallback
        return {
            "__model_name__": data["name"],
            "__model_module__": data["module"],
            "fields": data["fields"],
            "is_representation": True,
        }


# Register common serializers
SerializationRegistry.register(
    "pydantic.main.BaseModel", _serialize_pydantic_model, _deserialize_pydantic_model
)
SerializationRegistry.register(
    "pydantic.BaseModel", _serialize_pydantic_model, _deserialize_pydantic_model
)


def serialize_object(obj: Any) -> dict[str, Any]:
    """Serialize an object to a format suitable for storage.

    Args:
        obj: Object to serialize

    Returns:
        Serialized representation as a JSON-compatible dict
    """
    return SerializationRegistry.serialize(obj)


def deserialize_object(data: dict[str, Any]) -> Any:
    """Deserialize an object from stored data.

    Args:
        data: Serialized representation

    Returns:
        Deserialized object
    """
    return SerializationRegistry.deserialize(data)
