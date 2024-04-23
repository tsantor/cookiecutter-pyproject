import configparser
from pathlib import Path

import pkg_resources
from {{cookiecutter.package_dir}}.settings import copy_resource_file
from {{cookiecutter.package_dir}}.settings import get_config_value_as_list


def test_copy_resource_file(tmp_path):
    # Create a temp data file in the package resources
    temp_data_file = pkg_resources.resource_filename("{{cookiecutter.package_dir}}", "data/test.txt")

    source_file = Path(temp_data_file)
    source_file.parent.mkdir(parents=True, exist_ok=True)
    source_file.write_text("Test content")

    # Call copy_resource_file with the source file name and a destination path
    copy_resource_file("test.txt", str(tmp_path / "dest" / "test.txt"))

    # Check that the destination file exists and has the correct content
    dest_file = tmp_path / "dest" / "test.txt"
    assert dest_file.is_file()
    assert dest_file.read_text() == "Test content"

    # Remove the temp data file
    source_file.unlink()


def test_get_config_value_as_list():
    # Create a ConfigParser object and add a section with a key
    config = configparser.ConfigParser()
    config.add_section("default")
    config.set("default", "key_words", "item1, item2, item3")

    result = get_config_value_as_list(config, "default", "key_words")
    assert result == ["item1", "item2", "item3"]