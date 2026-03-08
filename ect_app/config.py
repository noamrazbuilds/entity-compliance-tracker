from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    database_url: str = "sqlite:///data/ect.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Frontend
    frontend_url: str = "http://localhost:8501"

    # CORS
    cors_origins: list[str] = ["http://localhost:8501", "http://localhost:3000"]

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""

    # Slack
    slack_webhook_url: str = ""

    # Reminder intervals (days before deadline)
    reminder_intervals_days: list[int] = [30, 14, 7]


settings = Settings()
