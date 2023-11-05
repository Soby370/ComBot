from typing import Any
from decouple import config

class ConfigHandler:
    BOT_TOKEN: str= config("BOT_TOKEN", default="", cast=str) # type: ignore
    OWNER_ID: int = config("OWNER_ID", cast=int, default=0)

    def __getattribute__(self, __name: str) -> Any:
        return config(__name, default="")

Config = ConfigHandler()