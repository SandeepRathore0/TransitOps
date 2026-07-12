from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    PROJECT_NAME: str = "TransitOps"
    DATABASE_URL: str = "mysql+pymysql://root:Gunjan2005%40@localhost/transitops"
    SECRET_KEY: str = "supersecretkey1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
settings = Settings()
