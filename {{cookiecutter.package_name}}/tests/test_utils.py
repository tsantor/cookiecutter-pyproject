from pathlib import Path

from {{cookiecutter.package_dir}}.utils import home_agnostic_path


def test_home_agnostic_path():
    home = Path.home()

    # Test with a path in the home directory
    path_in_home = home / "test"
    assert home_agnostic_path(str(path_in_home)) == "~/test"

    # Test with a path not in the home directory
    path_not_in_home = Path("/tmp/test")
    assert home_agnostic_path(str(path_not_in_home)) == str(path_not_in_home)
