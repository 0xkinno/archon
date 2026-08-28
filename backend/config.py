import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "ARCHON Enterprise Fleet"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # GCP & Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GCP_PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "archon-ece25")
    GCP_LOCATION: str = os.getenv("GCP_LOCATION", "us-central1")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")
    GOOGLE_APPLICATION_CREDENTIALS_JSON: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "")
    
    # Storage
    FIRESTORE_DATABASE: str = os.getenv("FIRESTORE_DATABASE", "(default)")
    FIRESTORE_EMULATOR_HOST: str = os.getenv("FIRESTORE_EMULATOR_HOST", "")
    
    # GEAP Governance Features
    USE_MEMORY_BANK: bool = os.getenv("USE_MEMORY_BANK", "false").lower() in ("true", "1", "yes")
    USE_AGENT_RUNTIME: bool = os.getenv("USE_AGENT_RUNTIME", "true").lower() in ("true", "1", "yes")
    USE_MODEL_ARMOR: bool = os.getenv("USE_MODEL_ARMOR", "true").lower() in ("true", "1", "yes")
    APPROVAL_THRESHOLD: float = float(os.getenv("APPROVAL_THRESHOLD", "10000.0"))
    RATE_LIMIT_TOOL_CALLS: int = int(os.getenv("RATE_LIMIT_TOOL_CALLS", "20"))
    
    # Security & Identity
    JWT_SECRET: str = os.getenv("JWT_SECRET", "archon_enterprise_secure_secret_key_2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    
    # Server & Networking
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://archon-app.vercel.app",
        "*"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
