import os
import re
import sys

import pytest

try:
    import sh
except (ImportError, ModuleNotFoundError):
    sh = None  # sh doesn't support Windows
from binaryornot.check import is_binary
from cookiecutter.exceptions import FailedHookException

PATTERN = r"{{(\s?cookiecutter)[.](.*?)}}"
RE_OBJ = re.compile(PATTERN)

if sys.platform.startswith("win"):
    pytest.skip("sh doesn't support windows", allow_module_level=True)
elif sys.platform.startswith("darwin") and os.getenv("CI"):
    pytest.skip("skipping slow macOS tests on CI", allow_module_level=True)

# Run auto-fixable styles checks - skipped on CI by default. These can be fixed
# automatically by running pre-commit after generation however they are tedious
# to fix in the template, so we don't insist too much in fixing them.
AUTOFIXABLE_STYLES = os.getenv("AUTOFIXABLE_STYLES") == "1"
auto_fixable = pytest.mark.skipif(not AUTOFIXABLE_STYLES, reason="auto-fixable")


@pytest.fixture
def context():
    return {
        "project_name": "My Awesome Package",
        "package_name": "my-python-package",
        "package_dir": "my_awesome_package",
        "author_name": "Test Author",
        "email": "test@example.com",
        "description": "A short description of the project.",
        "domain": "example.com",
        "version": "0.1.0",
        "github_username": "testuser",
        "use_sentry": "n",
        "has_cli": "y",
    }


SUPPORTED_COMBINATIONS = [
    {"open_source_license": "MIT"},
    {"open_source_license": "BSD"},
    {"open_source_license": "GPLv3"},
    {"open_source_license": "Apache Software License 2.0"},
    {"open_source_license": "Not open source"},
    {"use_sentry": "y"},
    {"use_sentry": "n"},
    {"has_cli": "y"},
    {"has_cli": "n"},
    {"use_rich": "y"},
    {"use_rich": "n"},
]

UNSUPPORTED_COMBINATIONS = []


def _fixture_id(ctx):
    """Helper to get a user-friendly test name from the parametrized context."""
    return "-".join(f"{key}:{value}" for key, value in ctx.items())


def build_files_list(base_dir):
    """Build a list containing absolute paths to the generated files."""
    return [
        os.path.join(dirpath, file_path)
        for dirpath, subdirs, files in os.walk(base_dir)
        for file_path in files
    ]


def check_paths(paths):
    """Method to check all paths have correct substitutions."""
    # Assert that no match is found in any of the files
    for path in paths:
        if is_binary(path):
            continue

        for line in open(path):
            match = RE_OBJ.search(line)
            assert match is None, f"cookiecutter variable not replaced in {path}"


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_project_generation(cookies, context, context_override):
    """Test that project is generated and fully rendered."""

    result = cookies.bake(extra_context={**context, **context_override})
    assert result.exit_code == 0
    assert result.exception is None
    assert result.project_path.name == context["package_name"]
    assert result.project_path.is_dir()

    paths = build_files_list(str(result.project_path))
    check_paths(paths)


@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_ruff_check_passes(cookies, context_override):
    """Generated project should pass ruff check."""
    result = cookies.bake(extra_context=context_override)

    try:
        sh.ruff("check", ".", "--fix", _cwd=str(result.project_path))
    except sh.ErrorReturnCode as e:
        pytest.fail(e.stdout.decode())


# @auto_fixable
@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_ruff_format_passes(cookies, context_override):
    """Check whether generated project passes ruff format."""
    result = cookies.bake(extra_context=context_override)

    try:
        sh.ruff(
            "format",
            ".",
            _cwd=str(result.project_path),
        )
    except sh.ErrorReturnCode as e:
        pytest.fail(e.stdout.decode())


# @auto_fixable
@pytest.mark.parametrize("context_override", SUPPORTED_COMBINATIONS, ids=_fixture_id)
def test_isort_passes(cookies, context_override):
    """Check whether generated project passes isort style."""
    result = cookies.bake(extra_context=context_override)

    try:
        sh.isort(_cwd=str(result.project_path))
    except sh.ErrorReturnCode as e:
        pytest.fail(e.stdout.decode())


@pytest.mark.parametrize("slug", ["Package Dir"])
def test_invalid_slug(cookies, context, slug):
    """Invalid slug should fail pre-generation hook."""
    context.update({"package_dir": slug})

    result = cookies.bake(extra_context=context)

    assert result.exit_code != 0
    assert isinstance(result.exception, FailedHookException)


@pytest.mark.parametrize("invalid_context", UNSUPPORTED_COMBINATIONS)
def test_error_if_incompatible(cookies, context, invalid_context):
    """It should not generate project an incompatible combination is selected."""
    context.update(invalid_context)
    result = cookies.bake(extra_context=context)

    assert result.exit_code != 0
    assert isinstance(result.exception, FailedHookException)


def test_trim_domain_email(cookies, context):
    """Check that leading and trailing spaces are trimmed in domain and email."""
    context.update(
        {
            "domain": "   example.com   ",
            "email": "  me@example.com  ",
        }
    )
    result = cookies.bake(extra_context=context)

    assert result.exit_code == 0
