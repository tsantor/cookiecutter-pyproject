from pathlib import Path

from cookiecutter.main import cookiecutter

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
    print(INFO + f"Removing {file_name} from src directory..." + TERMINATOR)
    dir = Path(PROJECT_DIRECTORY / "src" / "{{cookiecutter.package_dir}}")
    Path(dir / file_name).unlink()


def remove_open_source_files():
    """Remove open source files from generated project."""
    file_names = ["CONTRIBUTORS.txt", "LICENSE"]
    for file_name in file_names:
        print(INFO + f"Removing {file_name} from project..." + TERMINATOR)
        Path(PROJECT_DIRECTORY / file_name).unlink()


def remove_gplv3_files():
    """Remove GPL v3 files from generated project."""
    file_names = ["COPYING"]
    for file_name in file_names:
        print(INFO + f"Removing {file_name} from project..." + TERMINATOR)
        Path(PROJECT_DIRECTORY / file_name).unlink()


def remove_cli():
    """Remove CLI file from generated project."""
    remove_src_file("cli.py")
    remove_src_file("entrypoint.py")


def remove_settings():
    """Remove settings files from generated project."""
    remove_src_file("settings.py")
    remove_src_file("tests/test_settings.py")


def create_docs():
    """Create mkdocs project."""
    cookiecutter(
        "https://github.com/tsantor/cookiecutter-mkdocs.git",
        no_input=True,  # Avoid prompting the user again
        extra_context={
            "project_name": "{{ cookiecutter.project_name }}",
            "project_slug": "{{ cookiecutter.package_dir }}",
            "project_short_description": "{{ cookiecutter.project_short_description }}",
            "full_name": "{{ cookiecutter.author_name }}",
            "email": "{{ cookiecutter.email }}",
            "domain": "{{ cookiecutter.domain }}",
            "version": "{{ cookiecutter.version }}",
        },
        output_dir=".",  # Current directory of new project
    )
    # rename generated mkdocs directory


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
    create_docs()

    print(SUCCESS + "Project initialized, keep up the good work!" + TERMINATOR)


if __name__ == "__main__":
    main()
