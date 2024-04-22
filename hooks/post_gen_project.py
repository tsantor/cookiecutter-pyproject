#!/usr/bin/env python
from pathlib import Path

PROJECT_DIRECTORY = Path.cwd()

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

DEBUG_VALUE = "debug"

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def remove_open_source_files():
    file_names = ["CONTRIBUTORS.txt", "LICENSE"]
    for file_name in file_names:
        (PROJECT_DIRECTORY / file_name).unlink(missing_ok=True)


def remove_gplv3_files():
    file_names = ["COPYING"]
    for file_name in file_names:
        Path(file_name).unlink(missing_ok=True)


def remove_cli():
    (PROJECT_DIRECTORY / "src" / "{{cookiecutter.package_dir}}" / "cli.py").unlink(
        missing_ok=True
    )


def remove_file(filepath):
    """Remove file from generated project."""
    (PROJECT_DIRECTORY / filepath).unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    # print(PROJECT_DIRECTORY)

    if "{{ cookiecutter.open_source_license }}" == "Not open source":
        remove_open_source_files()

    if "{{ cookiecutter.open_source_license}}" != "GPLv3":
        remove_gplv3_files()

    if "{{ cookiecutter.has_cli }}".lower() == "n":
        remove_cli()

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()
