import re
import sys

TERMINATOR = "\x1b[0m"
WARNING = "\x1b[1;33m [WARNING]: "
INFO = "\x1b[1;33m [INFO]: "
HINT = "\x1b[3;33m"
SUCCESS = "\x1b[1;32m [SUCCESS]: "

MODULE_REGEX = r"^[_a-zA-Z][_a-zA-Z0-9]+$"

module_name = "{{ cookiecutter.package_dir }}"


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    if not re.match(MODULE_REGEX, module_name):
        print(
            f"ERROR: The project slug {module_name} is not a valid Python "
            "module name. Please do not use a - and use _ instead."
        )

        # Exit to cancel project
        sys.exit(1)

    # TODO: Maybe test for invalid options here in future

    # print(SUCCESS + "Pre-gen OK!" + TERMINATOR)


if __name__ == "__main__":
    main()
