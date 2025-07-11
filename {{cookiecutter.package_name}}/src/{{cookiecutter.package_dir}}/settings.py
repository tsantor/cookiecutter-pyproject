import shutil
from importlib import resources
from pathlib import Path

import toml

from .models import AppConfig
{%- if cookiecutter.use_sentry == "y" %}
from .models import SentryConfig
{% endif %}
from .mqtt.models import MQTTConfig

# -----------------------------------------------------------------------------
# PACKAGE CONSTANTS
# -----------------------------------------------------------------------------

APP_NAME: str = "{{cookiecutter.package_name}}"
PACKAGE_DIR: str = "{{cookiecutter.package_dir}}"
SETTINGS_DIR: Path = Path("~/.{{cookiecutter.package_name}}").expanduser()
CONFIG_FILE: Path = Path(f"{SETTINGS_DIR}/{APP_NAME}.toml")
LOG_FILE: Path = Path(f"{SETTINGS_DIR}/{APP_NAME}.log")

# -----------------------------------------------------------------------------


def copy_resource_file(filename, dst):
    """Copy data files from package data folder."""
    # Create destination dir if needed
    dir_path = Path(dst).parent
    if not dir_path.is_dir():
        dir_path.mkdir()

    # Copy data file to destination
    ref = resources.files(PACKAGE_DIR) / f"data/{filename}"
    with resources.as_file(ref) as src:
        dst = str(Path(dir_path).expanduser())
        shutil.copy2(src, dst)


if not CONFIG_FILE.exists():
    copy_resource_file(f"{APP_NAME}.toml", str(CONFIG_FILE))  # pragma: no cover

if not LOG_FILE.exists():
    LOG_FILE.touch()  # pragma: no cover

with CONFIG_FILE.open("r") as f:
    config = toml.load(f)

# -----------------------------------------------------------------------------

app_config = AppConfig(**config["default"])
{%- if cookiecutter.use_sentry == "y" %}
sentry_config = SentryConfig(**config.get("sentry", {}))
{%- endif %}
mqtt_config = MQTTConfig(**config.get("mqtt", {}))
