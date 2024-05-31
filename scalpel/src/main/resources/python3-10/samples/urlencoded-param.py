"""
    URL Decoding and Encoding for Parameters

    This script interacts with HTTP requests that contain urlencoded parameters. 
    It is useful when you need to view or modify urlencoded parameters in a more readable format. 
    The script provides functions to decode and encode the 'filename' and 'directory' query parameters.
"""

from pyscalpel import Request
from pyscalpel.utils import urldecode, urlencode_all


def req_edit_in_filename(req: Request) -> bytes | None:
    """
    URL decodes the 'filename' parameter from the request.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decoded 'filename' parameter.
    """
    param = req.query.get("filename")
    if param is not None:
        return urldecode(param)


def req_edit_out_filename(req: Request, text: bytes) -> Request | None:
    """
    URL encodes the 'filename' parameter for the outgoing request.

    Args:
        req: The outgoing HTTP request.
        text: The value to be URL encoded and set as the 'filename' parameter.

    Returns:
        The HTTP request with the newly URL encoded 'filename' parameter.
    """
    req.query["filename"] = urlencode_all(text)
    return req


def req_edit_in_directory(req: Request) -> bytes | None:
    """
    URL decodes the 'directory' parameter from the request.

    Args:
        req: The incoming HTTP request.

    Returns:
        The decoded 'directory' parameter.
    """
    param = req.query.get("directory")
    if param is not None:
        return urldecode(param)


def req_edit_out_directory(req: Request, text: bytes) -> Request | None:
    """
    URL encodes the 'directory' parameter for the outgoing request.

    Args:
        req: The outgoing HTTP request.
        text: The value to be URL encoded and set as the 'directory' parameter.

    Returns:
        The HTTP request with the newly URL encoded 'directory' parameter.
    """
    req.query["directory"] = urlencode_all(text)
    return req
