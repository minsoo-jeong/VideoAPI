from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_HOST:str = "127.0.0.1"
    API_PORT:int = 8888

    TRITON_HOST: str = "triton"
    TRITON_PORT: int = 8001

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


settings = Settings()
