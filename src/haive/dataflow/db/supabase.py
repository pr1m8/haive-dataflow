"""Supabase database integration for the Haive registry system.

This module provides functionality for connecting to and interacting with a
Supabase database instance for storing registry data. It handles connection
management, schema mapping, and query execution.

The module uses environment variables for configuration:
- SUPABASE_URL: The URL of your Supabase instance
- SUPABASE_SERVICE_KEY: Service role API key (preferred for admin operations)
- SUPABASE_ANON_KEY: Anonymous API key (fallback)

Typical usage example:

    >>> from haive.dataflow.db.supabase import get_supabase_client
    >>>
    >>> # Get a Supabase client
    >>> supabase = get_supabase_client()
    >>>
    >>> # Query a table
    >>> result = supabase.table('registry_items').select('*').execute()
    >>> items = result.data
    >>> print(f"Found {len(items)} registry items")
"""

import os
from typing import Any

from dotenv import load_dotenv
from supabase import Client, ClientOptions, create_client

# Load environment variables from .env file if present
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
# Use SERVICE_KEY primarily, only fall back to ANON_KEY if necessary
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    if os.getenv("SUPABASE_SERVICE_KEY")
    else os.getenv("SUPABASE_ANON_KEY")
)

# Map of table names to their schemas for common tables
DEFAULT_SCHEMA_MAP = {
    # Models schema (updated from your new schema structure)
    "providers": "models",
    "provider_types": "models",
    "llm_models": "models",
    "llm_capabilities": "models",
    "llm_pricing": "models",
    "embedding_models": "models",
    "embedding_pricing": "models",
    "vectorstore_providers": "models",
    "vectorstore_configurations": "models",
    "retriever_types": "models",
    "retriever_configurations": "models",
    "schemas": "models",
    # Engines schema
    "engine_types": "engines",
    "engines": "engines",
    "engine_versions": "engines",
    "runtime_configurations": "engines",
    "node_types": "engines",
    "node_instances": "engines",
    "node_middlewares": "engines",
    "engine_tools": "engines",
    "engine_schemas": "engines",
    # Agents schema
    "types": "agents",
    "agents": "agents",
    "agent_engines": "agents",
    "agent_tools": "agents",
    # Tools schema
    "categories": "tools",
    "tools": "tools",
    "toolkits": "tools",
    "toolkit_tools": "tools",
    # Config schema
    "component_types": "config",
    "components": "config",
    "environment_variables": "config",
    "component_env_mappings": "config",
    "env_var_detection_patterns": "config",
    # Registry schema (kept for backward compatibility)
    "items": "registry",
    "configurations": "registry",
    "dependencies": "registry",
    "environment_vars": "registry",
    # Audit schema
    "import_logs": "audit",
    "audit_logs": "audit",
    "runtime_logs": "audit",
    # Public schema (default)
    "threads": "public",
    "user_profiles": "public",
    "teams": "public",
    "team_members": "public",
    "api_keys": "public",
    "vault_secrets": "vault",
}


def get_supabase_client(schema: str | None = None) -> Client:
    """Get a configured Supabase client instance.

    Creates and returns a Supabase client configured with the specified schema.
    The client uses environment variables for connection parameters.

    Args:
        schema: Optional database schema to use. If not specified,
            defaults to "public" schema.

    Returns:
        Client: A configured Supabase client instance.

    Raises:
        EnvironmentError: If required environment variables are not set.

    Example:
        >>> # Get client with default schema
        >>> client = get_supabase_client()
        >>>
        >>> # Get client with specific schema
        >>> registry_client = get_supabase_client("registry")
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise OSError("Supabase URL or KEY not set in environment.")

    options = ClientOptions(
        schema=schema or "public",
        headers={"X-Client-Info": "haive-framework"},
    )

    return create_client(SUPABASE_URL, SUPABASE_KEY, options=options)


def parse_table_reference(table_ref: str) -> tuple[str, str | None]:
    """Parse a table reference to extract table name and schema.

    This function parses table references in various formats and extracts
    the table name and schema. It handles:
    - Simple table names: "items" (uses default schema mapping)
    - Schema-qualified names: "registry.items" (explicit schema)

    Args:
        table_ref: Table reference string in one of the supported formats.
            Examples: "items", "registry.items", "models.providers"

    Returns:
        Tuple[str, Optional[str]]: A tuple containing (table_name, schema_name),
            where schema_name may be None if not specified and not in DEFAULT_SCHEMA_MAP.

    Example:
        >>> parse_table_reference("items")
        ('items', 'registry')  # Uses default schema mapping
        >>> parse_table_reference("registry.items")
        ('items', 'registry')  # Explicit schema
        >>> parse_table_reference("custom_table")
        ('custom_table', None)  # No mapping found
    """
    parts = table_ref.split(".")
    if len(parts) == 1:
        # No schema specified, use the default mapping
        table_name = parts[0]
        schema = DEFAULT_SCHEMA_MAP.get(table_name)
        return table_name, schema
    if len(parts) == 2:
        # Schema explicitly specified
        schema, table_name = parts
        return table_name, schema
    raise ValueError(f"Invalid table reference: {table_ref}")


def table(client: Client, table_ref: str, schema_override: str | None = None) -> Any:
    """Get a table reference with appropriate schema handling.

    Args:
        client: Supabase client
        table_ref: Table reference (can include schema)
        schema_override: Optional schema to override detected schema

    Returns:
        Table reference for queries
    """
    # Parse the table reference
    table_name, schema = parse_table_reference(table_ref)

    # Use override if provided
    if schema_override:
        schema = schema_override

    # If we have a schema that's different from the client's schema,
    # create a new client with the right schema
    if schema and schema != getattr(client, "_schema", None):
        temp_client = get_supabase_client(schema)
        return temp_client.table(table_name)

    # Otherwise use the provided client
    return client.table(table_name)


def sanitize_sql(sql: str) -> str:
    """Remove trailing semicolons and whitespace for safe RPC use."""
    return sql.strip().rstrip(";").strip()


def fetch_all_schemas_and_tables(client: Client) -> list[dict]:
    """Return all non-system tables grouped by schema using raw SQL."""
    sql = """
        SELECT
            table_schema,
            table_name,
            table_type
        FROM
            information_schema.tables
        WHERE
            table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY
            table_schema, table_name
    """
    sql = sanitize_sql(sql)
    return client.rpc("execute_sql", {"sql": sql}).execute().data


def fetch_foreign_key_relations(client: Client) -> list[dict]:
    """Return foreign key relationships between tables using raw SQL."""
    sql = """
        SELECT
            tc.table_schema,
            tc.table_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE
            tc.constraint_type = 'FOREIGN KEY'
        ORDER BY
            tc.table_schema, tc.table_name
    """
    sql = sanitize_sql(sql)
    return client.rpc("execute_sql", {"sql": sql}).execute().data


def fetch_table_columns(client: Client) -> list[dict]:
    """Get all columns, types, and constraints from
    information_schema.columns.
    """
    sql = """
        SELECT
            table_schema,
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM
            information_schema.columns
        WHERE
            table_schema NOT IN ('information_schema', 'pg_catalog')
        ORDER BY
            table_schema, table_name, ordinal_position
    """
    sql = sanitize_sql(sql)
    return client.rpc("execute_sql", {"sql": sql}).execute().data


def fetch_primary_keys(client: Client) -> list[dict]:
    """Get all primary keys per table."""
    sql = """
        SELECT
            kcu.table_schema,
            kcu.table_name,
            tco.constraint_name,
            kcu.column_name
        FROM
            information_schema.table_constraints tco
            JOIN information_schema.key_column_usage kcu
              ON kcu.constraint_name = tco.constraint_name
        WHERE
            tco.constraint_type = 'PRIMARY KEY'
        ORDER BY
            kcu.table_schema, kcu.table_name, kcu.ordinal_position
    """
    sql = sanitize_sql(sql)
    return client.rpc("execute_sql", {"sql": sql}).execute().data
