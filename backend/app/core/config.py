"""
Application configuration.

All environment variables are loaded here.
No secrets in code, ever.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are validated via Pydantic.
    Missing required values will raise ValidationError at startup.
    """

    # Environment
    ENV: str = "local"  # local, development, production
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"

    # CORS (comma-separated string, parsed to list)
    # Default includes both common Vite dev ports
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS_ORIGINS string into list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Supabase (optional for development scaffolding)
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""  # Public anon key (if needed for client-side)
    SUPABASE_SERVICE_ROLE_KEY: str = ""  # Service role key (avoid in normal flows, RLS is boss)

    # Stripe (optional for development scaffolding)
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Sentry
    SENTRY_DSN: str | None = None

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = False  # Disabled by default in local dev

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra env vars to prevent accidental exposure
    )


# Global settings instance
# Will raise ValidationError if required env vars are missing
settings = Settings()
