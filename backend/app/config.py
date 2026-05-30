from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    llm_fallback_model: str = "deepseek-chat"
    llm_max_tokens: int = 4096
    llm_timeout: int = 30
    llm_concurrency: int = 5

    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "career_knowledge"

    data_provider: str = "demo"
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
