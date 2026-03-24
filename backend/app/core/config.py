"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI-Powered Customer Onboarding Portal"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/onboarding"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # JWT / Auth
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 15
    OTP_EXPIRY_SECONDS: int = 60
    MAX_OTP_ATTEMPTS: int = 5
    LOCKOUT_MINUTES: int = 15

    # AWS
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str = "onboarding-documents"
    S3_PRESIGNED_EXPIRY: int = 3600
    SES_SENDER_EMAIL: str = "noreply@example.com"
    SNS_TOPIC_ARN: str = ""
    COGNITO_USER_POOL_ID: str = ""
    COGNITO_CLIENT_ID: str = ""

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"
    OPENAI_TEMPERATURE: float = 0.1
    OPENAI_MAX_RETRIES: int = 3

    # Upload limits
    MAX_UPLOAD_SIZE_BYTES: int = 10_485_760  # 10 MB
    ALLOWED_FILE_TYPES: list[str] = ["application/pdf", "image/jpeg", "image/png"]

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
