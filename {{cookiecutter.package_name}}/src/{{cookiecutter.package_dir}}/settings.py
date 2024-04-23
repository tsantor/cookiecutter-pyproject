import configparser
import logging
import shutil
from pathlib import Path

import pkg_resources

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


def copy_resource_file(filename, dst):
    """Copy data files from package data folder."""
    # Create destination dir if needed
    dir_path = Path(dst).parent
    if not dir_path.is_dir():
        dir_path.mkdir()

    # Copy data file to destination
    src = pkg_resources.resource_filename("{{cookiecutter.package_dir}}", f"data/{filename}")
    dst = str(Path(dir_path).expanduser())
    shutil.copy2(src, dst)


CONFIG_FILE = Path(
    "~/.{{cookiecutter.package_name}}/{{cookiecutter.package_name}}.cfg"
).expanduser()
if not CONFIG_FILE.exists():
    copy_resource_file("{{cookiecutter.package_name}}.cfg", str(CONFIG_FILE))

LOG_FILE = Path(
    "~/.{{cookiecutter.package_name}}/{{cookiecutter.package_name}}.log"
).expanduser()
if not LOG_FILE.exists():
    LOG_FILE.touch()

# -----------------------------------------------------------------------------

def get_config_value_as_list(config: configparser.ConfigParser, section: str, key: str) -> list[str]:
    data_string = config[section][key]
    return [item.strip() for item in data_string.split(",")]

config = configparser.ConfigParser()
config.read(CONFIG_FILE)

{%- if cookiecutter.use_sentry == "y" %}
# Default
SENTRY_DSN = config.get("default", "sentry_dsn", fallback=None)
{%- endif %}
