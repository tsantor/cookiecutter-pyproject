from pathlib import Path

from pydantic import BaseModel, field_validator


class AppConfig(BaseModel):
    foo: str = None
    log_path: Path | None = None

    @field_validator(
        "log_path",
        mode="before",
    )
    def expand_user_paths(cls, v):  # noqa: N805
        return Path(v).expanduser() if v else None

{%- if cookiecutter.use_sentry == "y" %}
class SentryConfig(BaseModel):
    dsn: str | None = None
    environment: str = "production"
{%- endif %}
