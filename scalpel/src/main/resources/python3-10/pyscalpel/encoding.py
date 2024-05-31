"""
    Utilities for encoding data.
"""

from urllib.parse import unquote_to_bytes as urllibdecode
from _internal_mitmproxy.utils import strutils


# str/bytes conversion helpers from mitmproxy/http.py:
# https://github.com/mitmproxy/mitmproxy/blob/main/mitmproxy/http.py#:~:text=def-,_native,-(x%3A
def always_bytes(data: str | bytes | int, encoding="latin-1") -> bytes:
    """Convert data to bytes

    Args:
        data (str | bytes | int): The data to convert

    Returns:
        bytes: The converted bytes
    """
    if isinstance(data, int):
        data = str(data)
    return strutils.always_bytes(data, encoding, "surrogateescape")


def always_str(data: str | bytes | int, encoding="latin-1") -> str:
    """Convert data to string

    Args:
        data (str | bytes | int): The data to convert

    Returns:
        str: The converted string
    """
    if isinstance(data, int):
        return str(data)
    return strutils.always_str(data, encoding, "surrogateescape")



def urlencode_all(data: bytes | str, encoding="latin-1") -> bytes:
    """URL Encode all bytes in the given bytes object"""
    return "".join(f"%{b:02X}" for b in always_bytes(data, encoding)).encode(encoding)


def urldecode(data: bytes | str, encoding="latin-1") -> bytes:
    """URL Decode all bytes in the given bytes object"""
    return urllibdecode(always_bytes(data, encoding))
