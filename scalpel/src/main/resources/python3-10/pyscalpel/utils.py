import inspect
from typing import TypeVar, Union
from pyscalpel.burp_utils import (
    urldecode,
    urlencode_all,
)


T = TypeVar("T", str, bytes)


def removeprefix(s: T, prefix: Union[str, bytes]) -> T:
    if isinstance(s, str) and isinstance(prefix, str):
        if s.startswith(prefix):
            return s[len(prefix) :]  # type: ignore
    elif isinstance(s, bytes) and isinstance(prefix, bytes):
        if s.startswith(prefix):
            return s[len(prefix) :]  # type: ignore
    return s


def removesuffix(s: T, suffix: Union[str, bytes]) -> T:
    if isinstance(s, str) and isinstance(suffix, str):
        if s.endswith(suffix):
            return s[: -len(suffix)]
    elif isinstance(s, bytes) and isinstance(suffix, bytes):
        if s.endswith(suffix):
            return s[: -len(suffix)]
    return s


def current_function_name() -> str:
    """Get current function name

    Returns:
        str: The function name
    """
    frame = inspect.currentframe()
    if frame is None:
        return ""

    caller_frame = frame.f_back
    if caller_frame is None:
        return ""

    return caller_frame.f_code.co_name


def get_tab_name() -> str:
    """Get current editor tab name

    Returns:
        str: The tab name
    """
    frame = inspect.currentframe()
    prefixes = ("req_edit_in", "req_edit_out")

    # Go to previous frame till the editor name is found
    while frame is not None:
        frame_name = frame.f_code.co_name
        for prefix in prefixes:
            if frame_name.startswith(prefix):
                return removeprefix(removeprefix(frame_name, prefix), "_")

        frame = frame.f_back

    raise RuntimeError("get_tab_name() wasn't called from an editor callback.")


__all__ = [
    "urldecode",
    "urlencode_all",
    "current_function_name",
]
