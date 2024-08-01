from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_HOST: str = "main"
    API_PORT: int = 8888

    TRITON_HOST: str = "triton"
    TRITON_PORT: int = 8001

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379


settings = Settings()
# for dev
settings.API_HOST = 'dev'
settings.TRITON_HOST = 'triton-dev'
settings.REDIS_HOST = 'localhost'
