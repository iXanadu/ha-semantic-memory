from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "HAMEM_", "env_file": ".env", "env_file_encoding": "utf-8"}

    # PostgreSQL
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ha_memory"
    db_user: str = "hamem"
    db_password: str = "hamem"

    # Ollama
    ollama_url: str = "http://localhost:11434"
    embed_model: str = "nomic-embed-text"

    # Server
    host: str = "0.0.0.0"
    port: int = 8920
    log_level: str = "info"

    # Optional API token — if set, all requests must include Authorization: Bearer <token>
    api_token: str = ""

    # Search tuning
    vector_threshold: float = 0.35
    trigram_weight: float = 0.15
    trigram_threshold: float = 0.1

    @property
    def dsn(self) -> str:
        if self.db_password:
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        return f"postgresql://{self.db_user}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
