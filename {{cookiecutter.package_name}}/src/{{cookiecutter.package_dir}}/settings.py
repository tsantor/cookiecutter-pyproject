import logging
import shutil
from pathlib import Path

import pkg_resources
import toml
from pydantic_settings import BaseSettings

logger = logging.getLogger("{{cookiecutter.package_name}}")

# -----------------------------------------------------------------------------
# PACKAGE CONSTANTS
# -----------------------------------------------------------------------------

APP_NAME: str = "{{cookiecutter.package_name}}"
PACKAGE_DIR: str = "{{cookiecutter.package_dir}}"
CONFIG_FILE: Path = Path(f"~/.{APP_NAME}/{APP_NAME}.toml").expanduser()
LOG_FILE: Path = Path(f"~/.{APP_NAME}/{APP_NAME}.log").expanduser()

# -----------------------------------------------------------------------------


def copy_resource_file(filename, dst):
    """Copy data files from package data folder."""
    # Create destination dir if needed
    dir_path = Path(dst).parent
    if not dir_path.is_dir():
        dir_path.mkdir()

    # Copy data file to destination
    src = pkg_resources.resource_filename(PACKAGE_DIR, f"data/{filename}")
    dst = str(Path(dir_path).expanduser())
    shutil.copy2(src, dst)


if not CONFIG_FILE.exists():
    copy_resource_file(f"{APP_NAME}.toml", str(CONFIG_FILE))  # pragma: no cover

if not LOG_FILE.exists():
    LOG_FILE.touch()  # pragma: no cover

with CONFIG_FILE.open("r") as f:
    config = toml.load(f)

# -----------------------------------------------------------------------------

{%- if cookiecutter.use_sentry == "y" %}
# SENTRY_DSN = config["default"]["sentry_dsn"]
{%- endif %}


class AppConfig(BaseSettings):
    """Application configuration."""
    {%- if cookiecutter.use_sentry == "y" %}
    sentry_dsn: str = None
    {%- endif %}
    foo: str = None


app_config = AppConfig(**config["default"])
logger.info("Config: %s", app_config)
