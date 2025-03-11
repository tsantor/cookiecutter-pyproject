import shutil
from pathlib import Path

PROJECT_DIRECTORY = Path.cwd()

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def remove_src_file(file_name):
    """Remove file from generated project."""
    dir = Path(PROJECT_DIRECTORY / "src" / "{{cookiecutter.package_dir}}")
    Path(dir / file_name).unlink()


def remove_open_source_files():
    """Remove open source files from generated project."""
    file_names = ["CONTRIBUTORS.txt", "LICENSE"]
    for file_name in file_names:
        Path(PROJECT_DIRECTORY / file_name).unlink()


def remove_gplv3_files():
    """Remove GPL v3 files from generated project."""
    file_names = ["COPYING"]
    for file_name in file_names:
        Path(PROJECT_DIRECTORY / file_name).unlink()


def remove_cli():
    """Remove CLI file from generated project."""
    remove_src_file("cli.py")
    remove_src_file("entrypoint.py")


def remove_settings():
    """Remove settings files from generated project."""
    remove_src_file("settings.py")
    remove_src_file("tests/test_settings.py")


def copy_license():
    """Copy LICENSE file to mkdocs/docs/license.md."""
    src = Path(PROJECT_DIRECTORY / "LICENSE")
    dst = Path(PROJECT_DIRECTORY / "mkdocs" / "docs" / "license.md")
    shutil.copy2(src, dst)


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main():
    """Main entry point."""

    if "{{ cookiecutter.open_source_license }}" == "Not open source":
        remove_open_source_files()

    if "{{ cookiecutter.open_source_license}}" != "GPLv3":
        remove_gplv3_files()

    if "{{ cookiecutter.has_cli }}".lower() == "n":
        remove_cli()

    # if "".lower() == "n":
    #     remove_settings()

    # MkDocs
    # copy_license()

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()
