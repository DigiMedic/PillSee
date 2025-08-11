"""
Configuration management pro PillSee backend
Centralizované nastavení pro celou aplikaci
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Aplikační nastavení z environment variables"""
    
    # Application
    app_name: str = "PillSee API"
    app_version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_embedding_model: str = "text-embedding-3-small"
    openai_vision_model: str = "gpt-4-vision-preview"
    openai_text_model: str = "gpt-4o-mini"
    
    # Supabase
    supabase_url: str = Field(..., env="SUPABASE_URL") 
    supabase_anon_key: str = Field(..., env="SUPABASE_ANON_KEY")
    supabase_service_key: str = Field(default="", env="SUPABASE_SERVICE_KEY")
    
    # Vector Store
    vector_table_name: str = "medications"
    vector_query_name: str = "match_medications"
    embedding_dimensions: int = 512
    
    # SÚKL Data
    sukl_data_url: str = Field(default="https://opendata.sukl.cz/", env="SUKL_DATA_URL")
    sukl_update_interval_hours: int = Field(default=24, env="SUKL_UPDATE_INTERVAL_HOURS")
    
    # Rate Limiting
    text_query_limit: str = Field(default="10/minute", env="TEXT_QUERY_LIMIT")
    image_query_limit: str = Field(default="5/minute", env="IMAGE_QUERY_LIMIT")
    
    # CORS - jako string, parsuje se později
    allowed_origins: str = Field(
        default="http://localhost:3000,https://pillsee.vercel.app",
        env="ALLOWED_ORIGINS"
    )
    
    # Security
    session_timeout_minutes: int = 30
    max_query_length: int = 500
    max_image_size_mb: int = 10
    
    # AI Processing
    confidence_thresholds: dict = {
        "high": 0.8,
        "medium": 0.6, 
        "low": 0.4
    }
    
    # Medical Disclaimer
    medical_disclaimer: str = """
    UPOZORNĚNÍ: Tyto informace slouží pouze pro informativní účely a nenahrazují 
    odbornou lékařskou radu, diagnózu nebo léčbu. Vždy se poraďte s kvalifikovaným 
    zdravotnickým odborníkem před užitím jakéhokoliv léku.
    """
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from string"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

# Globální instance nastavení
settings = Settings()

# Validace kritických nastavení
def validate_settings():
    """Validace že všechna kritická nastavení jsou správně nastavená"""
    
    required_settings = [
        ("openai_api_key", "OPENAI_API_KEY"),
        ("supabase_url", "SUPABASE_URL"),
        ("supabase_anon_key", "SUPABASE_ANON_KEY")
    ]
    
    missing = []
    for setting_name, env_var in required_settings:
        if not getattr(settings, setting_name, None):
            missing.append(env_var)
    
    if missing:
        raise ValueError(
            f"Chybí povinné environment variables: {', '.join(missing)}\n"
            f"Zkopírujte .env.example do .env a vyplňte hodnoty."
        )

# Automatická validace při importu
try:
    validate_settings()
except ValueError as e:
    if settings.environment == "development":
        print(f"⚠️  Configuration Warning: {e}")
    else:
        raise
