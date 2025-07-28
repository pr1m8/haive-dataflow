"""Environment configuration module.

This module provides environment functionality for the Haive framework.

Classes:
    SupabaseClientConfig: SupabaseClientConfig implementation.
    SupabaseServerConfig: SupabaseServerConfig implementation.
    PostgresConfig: PostgresConfig implementation.

Functions:
    get_connection_uri: Get Connection Uri functionality.
    get_supabase_client_config: Get Supabase Client Config functionality.
    get_supabase_server_config: Get Supabase Server Config functionality.
"""

# haive_dataflow/config/environment.py
import os

from pydantic import BaseModel, Field, SecretStr


class SupabaseClientConfig(BaseModel):
    """Frontend-facing Supabase client configuration."""

    url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    anon_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("SUPABASE_ANON_KEY", ""))
    )


class SupabaseServerConfig(BaseModel):
    """Backend-only Supabase server configuration."""

    url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    service_role_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("SUPABASE_SERVICE_KEY", ""))
    )
    audience: str = "authenticated"  # Default value
    jwt_secret: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("SUPABASE_JWT_SECRET", ""))
    )
    postgres_connection: str | None = Field(
        default_factory=lambda: os.getenv("SUPABASE_POSTGRES_CONNECTION", "")
    )


class PostgresConfig(BaseModel):
    """PostgreSQL configuration for direct connections."""

    host: str = Field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    user: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    password: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("POSTGRES_PASSWORD", ""))
    )
    database: str = Field(default_factory=lambda: os.getenv("POSTGRES_DB", "postgres"))
    ssl_mode: str | None = Field(
        default_factory=lambda: os.getenv("POSTGRES_SSL_MODE", "disable")
    )

    def get_connection_uri(self) -> str:
        """Get database connection URI."""
        from urllib.parse import quote_plus

        password = quote_plus(self.password.get_secret_value())

        uri = f"postgresql://{self.user}:{password}@{self.host}:{self.port}/{self.database}"
        if self.ssl_mode:
            uri += f"?sslmode={self.ssl_mode}"
        return uri


def get_supabase_client_config() -> SupabaseClientConfig:
    """Get Supabase client configuration from environment."""
    return SupabaseClientConfig()


def get_supabase_server_config() -> SupabaseServerConfig:
    """Get Supabase server configuration from environment."""
    return SupabaseServerConfig()


def get_postgres_config() -> PostgresConfig:
    """Get PostgreSQL configuration from environment."""
    return PostgresConfig()
