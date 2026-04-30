from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "mieSEARCH"
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/mie_search_index_db"
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_QUEUE: str = "global_search_updates"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    
    JWT_SECRET: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX: str = "unified_search"

    class Config:
        env_file = ".env"

settings = Settings()
