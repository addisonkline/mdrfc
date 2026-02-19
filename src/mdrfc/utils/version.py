from importlib import metadata


def get_mdrfc_version() -> str:
    """
    Get the current version of the mdrfc package.
    """
    version = metadata.version("mdrfc")
    return version