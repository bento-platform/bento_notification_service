from functools import lru_cache
from pathlib import Path
from typing import Annotated

from bento_lib.config.pydantic import BentoFastAPIBaseConfig
from bento_lib.service_info.types import BentoExtraServiceInfo
from fastapi import Depends
from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import SettingsConfigDict

from .constants import APP_DIR, BENTO_SERVICE_KIND, GIT_REPOSITORY, SERVICE_NAME, SERVICE_TYPE

__all__ = [
    "BENTO_EXTRA_SERVICE_INFO",
    "Config",
    "get_config",
    "ConfigDep",
]

BENTO_EXTRA_SERVICE_INFO: BentoExtraServiceInfo = {
    "serviceKind": BENTO_SERVICE_KIND,
    "gitRepository": GIT_REPOSITORY,
}


class Config(BentoFastAPIBaseConfig):
    model_config = SettingsConfigDict(extra="ignore", frozen=True)

    service_id: str = ":".join(SERVICE_TYPE.values())
    service_name: str = SERVICE_NAME
    service_description: str = "Notification service for a Bento platform node."

    # (Misleadingly named) path to the **directory** in which db.sqlite3 can be found or created.
    database: Path = APP_DIR.parent

    redis_host: str = "localhost"
    redis_port: int = 6379

    # AUTHZ_ENABLED is the legacy (pre-FastAPI) name for this variable
    bento_authz_enabled: bool = Field(True, validation_alias=AliasChoices("BENTO_AUTHZ_ENABLED", "AUTHZ_ENABLED"))
    # Only required if authorization is enabled - checked below.
    bento_authz_service_url: str = ""

    @model_validator(mode="after")
    def _check_authz_url_set_if_enabled(self):
        if self.bento_authz_enabled and not self.bento_authz_service_url.strip():
            raise ValueError("BENTO_AUTHZ_SERVICE_URL must be set when authorization is enabled")
        return self

    @property
    def database_url(self) -> str:
        return f"sqlite:///{self.database / 'db.sqlite3'}"


@lru_cache
def get_config() -> Config:
    return Config()


ConfigDep = Annotated[Config, Depends(get_config)]
