import logging
import shutil
from importlib import resources
from pathlib import Path

import toml
from pydantic import BaseModel
from pydantic import ValidationError

from .models import AppConfig
from .mqtt.models import MQTTConfig

{%- if cookiecutter.use_sentry == "y" %}
from .models import SentryConfig
{% endif %}
from .mqtt.models import MQTTConfig

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# PACKAGE CONSTANTS
# -----------------------------------------------------------------------------

APP_NAME: str = "{{cookiecutter.package_name}}"
PACKAGE_DIR: str = "{{cookiecutter.package_dir}}"
SETTINGS_DIR: Path = Path.home() / f".{APP_NAME}"
CONFIG_FILE: Path = SETTINGS_DIR / f"{APP_NAME}.toml"
LOG_FILE: Path = SETTINGS_DIR / f"{APP_NAME}.log"

# -----------------------------------------------------------------------------
# Configuration File Setup
# -----------------------------------------------------------------------------


def ensure_config_file() -> None:
    """Ensure the configuration file exists, copying from package data if needed."""
    if CONFIG_FILE.exists():
        return

    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        src_path = resources.files(PACKAGE_DIR) / "data" / f"{APP_NAME}.toml"
        with resources.as_file(src_path) as src:
            if not src.exists():
                msg = f"Configuration template {src} not found"
                raise FileNotFoundError(msg)
            shutil.copy2(src, CONFIG_FILE)
        logger.info("Created configuration file at %s", CONFIG_FILE)
    except (OSError, PermissionError) as e:
        logger.error("Failed to create configuration file %s: %s", CONFIG_FILE, e)  # noqa: TRY400
        raise


# -----------------------------------------------------------------------------
# Configuration Models
# -----------------------------------------------------------------------------


class Settings(BaseModel):
    """Application configuration loaded from TOML."""

    app: AppConfig
    sentry: SentryConfig
    mqtt: MQTTConfig

# -----------------------------------------------------------------------------
# Configuration Access
# -----------------------------------------------------------------------------


def load_config() -> Settings:
    """Load and return the configuration instance."""
    ensure_config_file()

    try:
        with CONFIG_FILE.open("r") as f:
            data = toml.load(f)
        return Settings(**data)
    except ValidationError:
        logger.exception("Configuration validation failed")
        raise
    except Exception:
        logger.exception("Failed to load configuration")
        raise
