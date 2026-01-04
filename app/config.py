from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_user : str
    database_password: str
    database_host: str
    database_port: int
    database_name: str
    secret_key: str
    algorithm: str
    access_token_expiration_time: int
    class Config:
        env_file = ".env"

settings = Settings() # type: ignore