from pathlib import Path


def home_agnostic_path(path: str) -> str:
    """Replace the home directory in the given path with a tilde."""
    home = Path.home()
    path = Path(path)
    try:
        # Use relative_to to get the relative path to the home directory
        relative_path = path.relative_to(home)
        return f"~/{relative_path}"
    except ValueError:
        # The path is not a subpath of the home directory
        return str(path)
