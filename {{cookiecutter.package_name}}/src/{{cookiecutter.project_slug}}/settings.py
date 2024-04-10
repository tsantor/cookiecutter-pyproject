import configparser
import logging
import shutil
from pathlib import Path

import pkg_resources

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------


def copy_file(filename, dst):
    """Copy data files from data folder."""
    # Create destination dir if needed
    dir_path = Path(dst).parent
    if not dir_path.is_dir():
        dir_path.mkdir()

    # Copy data file to destination
    src = pkg_resources.resource_filename(
        "{{cookiecutter.project_slug}}", f"data/{filename}"
    )
    dst = str(Path(dir_path).expanduser())
    shutil.copy2(src, dst)


CONFIG_FILE = Path(
    "~/.{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}.cfg"
).expanduser()
if not CONFIG_FILE.exists():
    copy_file("{{cookiecutter.project_slug}}.cfg", str(CONFIG_FILE))

LOG_FILE = Path(
    "~/.{{cookiecutter.project_slug}}/{{cookiecutter.project_slug}}.log"
).expanduser()
if not LOG_FILE.exists():
    LOG_FILE.touch()

# -----------------------------------------------------------------------------


config = configparser.ConfigParser()
config.read(CONFIG_FILE)

{%- if cookiecutter.use_sentry == "y" %}
# Default
SENTRY_DSN = config.get("default", "sentry_dsn", fallback=None)
{%- endif %}
