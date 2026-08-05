from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_id: int
    api_hash: str
    phone_number: str
    password: str
    poop_user_ids: str = ""
    gemini_api_key: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
