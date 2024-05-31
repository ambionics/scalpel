"""
This module provides reimplementations of Python virtual environnements scripts

This is designed to be used internally, 
but in the case where the user desires to dynamically switch venvs using this,
they should ensure the selected venv has the dependencies required by Scalpel.
"""

import os
import sys
import glob
import subprocess

_old_prefix = sys.prefix
_old_exec_prefix = sys.exec_prefix

# Python's virtualenv's activate/deactivate ported from the bash script to Python code.
# https://docs.python.org/3/library/venv.html#:~:text=each%20provided%20path.-,How%20venvs%20work%C2%B6,-When%20a%20Python

# pragma: no cover


def deactivate() -> None:  # pragma: no cover
    """Deactivates the current virtual environment."""
    if "_OLD_VIRTUAL_PATH" in os.environ:
        os.environ["PATH"] = os.environ["_OLD_VIRTUAL_PATH"]
        del os.environ["_OLD_VIRTUAL_PATH"]
    if "_OLD_VIRTUAL_PYTHONHOME" in os.environ:
        os.environ["PYTHONHOME"] = os.environ["_OLD_VIRTUAL_PYTHONHOME"]
        del os.environ["_OLD_VIRTUAL_PYTHONHOME"]
    if "VIRTUAL_ENV" in os.environ:
        del os.environ["VIRTUAL_ENV"]

    sys.prefix = _old_prefix
    sys.exec_prefix = _old_exec_prefix


def activate(path: str | None) -> None:  # pragma: no cover
    """Activates the virtual environment at the given path."""
    deactivate()

    if path is None:
        return

    virtual_env = os.path.abspath(path)
    os.environ["_OLD_VIRTUAL_PATH"] = os.environ.get("PATH", "")
    os.environ["VIRTUAL_ENV"] = virtual_env

    old_pythonhome = os.environ.pop("PYTHONHOME", None)
    if old_pythonhome:
        os.environ["_OLD_VIRTUAL_PYTHONHOME"] = old_pythonhome

    if os.name == "nt":
        site_packages_paths = os.path.join(virtual_env, "Lib", "site-packages")
    else:
        site_packages_paths = glob.glob(
            os.path.join(virtual_env, "lib", "python*", "site-packages")
        )

    if not site_packages_paths:
        raise RuntimeError(
            f"No 'site-packages' directory found in virtual environment at {virtual_env}"
        )

    site_packages = site_packages_paths[0]
    sys.path.insert(0, site_packages)
    sys.prefix = virtual_env
    sys.exec_prefix = virtual_env


def install(*packages: str) -> int:  # pragma: no cover
    """Install a Python package in the current venv.

    Returns:
        int: The pip install command exit code.
    """
    pip = os.path.join(sys.prefix, "bin", "pip")
    return subprocess.call([pip, "install", "--require-virtualenv", "--", *packages])


def uninstall(*packages: str) -> int:  # pragma: no cover
    """Uninstall a Python package from the current venv.

    Returns:
        int: The pip uninstall command exit code.
    """
    pip = os.path.join(sys.prefix, "bin", "pip")
    return subprocess.call(
        [pip, "uninstall", "--require-virtualenv", "-y", "--", *packages]
    )


def create(path: str) -> int:  # pragma: no cover
    """Creates a Python venv on the given path

    Returns:
        int: The `python3 -m venv` command exit code.
    """
    return subprocess.call(["python3", "-m", "venv", "--", path])


def create_default() -> str:  # pragma: no cover
    """Creates a default venv in the user's home directory
        Only creates it if the directory doesn't already exist

    Returns:
        str: The venv directory path.
    """
    scalpel_venv = os.path.join(os.path.expanduser("~"), ".scalpel", "venv_default")
    # Don't recreate the venv if it alreay exists
    if not os.path.exists(scalpel_venv):
        os.makedirs(scalpel_venv, exist_ok=True)
        create(scalpel_venv)
    return scalpel_venv
