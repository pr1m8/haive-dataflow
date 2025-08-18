"""Database module for Haive Dataflow.

This module provides database connectivity and operations for the Haive dataflow
system, including Supabase integration and database schema management.

Components:
    supabase: Supabase database connection and operations
    schema: Database schema definitions
    inspect_supabase: Supabase inspection utilities

Example:
    Basic usage::

        from haive.dataflow.db import supabase
        from haive.dataflow.db.schema import DatabaseSchema

"""

from . import supabase
from . import schema

__all__ = [
    "supabase",
    "schema",
]
