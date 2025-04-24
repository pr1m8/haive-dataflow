# haive_dataflow/config/environment.py
import os
from pydantic import BaseModel, Field, SecretStr
from typing import Optional, Dict, Any

class SupabaseClientConfig(BaseModel):
    """Frontend-facing Supabase client configuration."""
    url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    anon_key: SecretStr = Field(default_factory=lambda: SecretStr(os.getenv("SUPABASE_ANON_KEY", "")))

class SupabaseServerConfig(BaseModel):
    """Backend-only Supabase server configuration."""
    url: str = Field(default_factory=lambda: os.getenv("SUPABASE_URL", ""))
    service_role_key: SecretStr = Field(
        default_factory=lambda: SecretStr(os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""))
    )
    jwt_secret: SecretStr = Field(default_factory=lambda: SecretStr(os.getenv("SUPABASE_JWT_SECRET", "")))
    postgres_connection: Optional[str] = Field(
        default_factory=lambda: os.getenv("SUPABASE_POSTGRES_CONNECTION", "")
    )

class PostgresConfig(BaseModel):
    """PostgreSQL configuration for direct connections."""
    host: str = Field(default_factory=lambda: os.getenv("POSTGRES_HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.getenv("POSTGRES_PORT", "5432")))
    user: str = Field(default_factory=lambda: os.getenv("POSTGRES_USER", "postgres"))
    password: SecretStr = Field(default_factory=lambda: SecretStr(os.getenv("POSTGRES_PASSWORD", "")))
    database: str = Field(default_factory=lambda: os.getenv("POSTGRES_DB", "postgres"))
    ssl_mode: Optional[str] = Field(default_factory=lambda: os.getenv("POSTGRES_SSL_MODE", "disable"))

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