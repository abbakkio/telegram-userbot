from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_id: int
    api_hash: str
    phone_number: str
    password: str
    poop_user_ids: str = ""
    gemini_api_key: str = ""
    base_last_name: str = ""
    cv_api_url: str = "http://localhost:8000"
    cv_api_key: str = "status-secret-change-me"
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
