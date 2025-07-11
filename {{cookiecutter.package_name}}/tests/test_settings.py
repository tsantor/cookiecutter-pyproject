import importlib.resources

from {{cookiecutter.package_dir}}.settings import copy_resource_file


def test_copy_resource_file(tmp_path):
    # Create a temp data file in the package resources
    with importlib.resources.path("{{cookiecutter.package_dir}}.data", "test.txt") as source_file:
        source_file.parent.mkdir(parents=True, exist_ok=True)
        source_file.write_text("Test content")

        # Call copy_resource_file with the source file name and a destination path
        copy_resource_file("test.txt", str(tmp_path / "dest" / "test.txt"))

        # Check that the destination file exists and has the correct content
        dest_file = tmp_path / "dest" / "test.txt"
        assert dest_file.is_file()
        assert dest_file.read_text() == "Test content"
