from functools import lru_cache
from typing import Optional
from pydantic import BaseSettings, SecretStr, EmailStr
from pathlib import Path

from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class Settings(BaseSettings):
    APP_DIR = Path(__file__).parent
    # SERVICE_ACCOUNT_CRED_PATH = APP_DIR.joinpath(
    #     '../.config/god-horse-352a0c8228c0.json').absolute()
    IMG_DIR = Path('/tmp').joinpath('files')
    IMG_DIR = APP_DIR.joinpath('files')
    APP_NAME: str = 'God Hourse API'
    FROM_EMAIL: str = 'whighwall@gmail.com'
    SHEET_FILE_NAME: str = '神駒團箴言集'
    SHEET_CERT_CONF_NAME = 'cert_conf'
    ENV: Environment = Environment.DEVELOPMENT
    SENTRY_DSN: SecretStr = None
    API_KEY: SecretStr = "god-horse"
    DEFAULT_EMAIL_ADDRESS: EmailStr = "whighwall@email.com"
    SENDGRID_API_KEY: SecretStr = "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"
    BROKER_URL: str = "amqp://rabbitmq:rabbitmq@localhost"
    BROKER_POOL_LIMIT: Optional[int] = 1
    TEMPLATES_FOLDER: str = "templates"
    DETA_KEY = 'a0mi2jh3_YrH1DMoj9PdByadLxQ4rJd8erZ5jSP13'
    DETA_ID = 'a0mi2jh3'

    class Config:
        env_file = ".env"
        case_sensitive = True
        fields = {"BROKER_URL": {"env": ["BROKER_URL", "CLOUDAMQP_URL"]}}


@lru_cache()
def get_settings():
    return Settings()
