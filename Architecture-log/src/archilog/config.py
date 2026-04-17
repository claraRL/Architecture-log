import os
from dataclasses import dataclass

@dataclass
class Config:

    DATABASE_URL: str
    DEBUG: bool
    SECRET_KEY: str

config = Config(
    DATABASE_URL=os.getenv("ARCHILOG_DATABASE_URL", "sqlite:///data.db"),
    DEBUG=os.getenv("ARCHILOG_DEBUG", "False") == "True",
    SECRET_KEY= os.getenv("SECRET_KEY", "key-secrete")
)