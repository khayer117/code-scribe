from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./codescribe.db"
    CHROMA_DB_PATH: str = "./chroma_db"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.1:8b"
    OLLAMA_TIMEOUT: int = 120
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_COLLECTION: str = "icd10pcs_codes"
    TOP_K_RESULTS: int = 10
    RERANK_CANDIDATES: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
