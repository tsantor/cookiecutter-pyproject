import logging
import shutil
from pathlib import Path

import pkg_resources
import toml

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
    "~/.{{cookiecutter.package_name}}/{{cookiecutter.package_name}}.toml"
).expanduser()
if not CONFIG_FILE.exists():
    copy_resource_file("{{cookiecutter.package_name}}.toml", str(CONFIG_FILE))  # pragma: no cover

LOG_FILE = Path(
    "~/.{{cookiecutter.package_name}}/{{cookiecutter.package_name}}.log"
).expanduser()
if not LOG_FILE.exists():
    LOG_FILE.touch()  # pragma: no cover

# -----------------------------------------------------------------------------

with CONFIG_FILE.open("r") as f:
    config = toml.load(f)

{%- if cookiecutter.use_sentry == "y" %}
SENTRY_DSN = config["default"]["sentry_dsn"]
{%- endif %}

FOO = config["default"]["foo"]
