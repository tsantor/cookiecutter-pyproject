from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    foo: str = None
    log_path: Optional[Path] = None  # noqa: UP007

    @field_validator(
        "log_path",
        mode="before",
    )
    def expand_user_paths(cls, v):  # noqa: N805
        return Path(v).expanduser() if v else None


class SentryConfig(BaseSettings):
    dsn: Optional[str] = None  # noqa: UP007
    env: str = "production"
