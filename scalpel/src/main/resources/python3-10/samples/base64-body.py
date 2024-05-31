"""
    Base64 Encoding and Decoding

    This script is designed to handle incoming and outgoing HTTP requests/responses
    that may contain base64-encoded data in their contents. 

    It first tries to decode the contents using base64. If the content is not base64-encoded
    (i.e., if a binascii.Error exception is thrown), it leaves the content as it is. 

    When the request/response is sent back out, it encodes the content using base64. 
"""

from base64 import b64decode, b64encode
import binascii
from pyscalpel import Request, Response


def req_edit_in(req: Request) -> bytes:
    """
    Tries to decode the content of the incoming HTTP request using base64.

    Args:
        req: The incoming HTTP request.

    Returns:
        The base64-decoded content of the HTTP request, or the original content if it wasn't base64-encoded.
    """
    if req.content:
        try:
            req.content = b64decode(req.content, validate=True)
        except binascii.Error:
            pass

    return req.content or b""


def req_edit_out(req: Request, text: bytes) -> Request:
    """
    Encodes the content of the outgoing HTTP request using base64.

    Args:
        req: The outgoing HTTP request.
        text: The content to be base64-encoded.

    Returns:
        The HTTP request with the base64-encoded content.
    """
    if req.content:
        req.content = b64encode(text)
    return req


def res_edit_in(res: Response) -> bytes:
    """
    Tries to decode the content of the incoming HTTP response using base64.

    Args:
        res: The incoming HTTP response.

    Returns:
        The base64-decoded content of the HTTP response, or the original content if it wasn't base64-encoded.
    """
    if res.content:
        try:
            res.content = b64decode(res.content, validate=True)
        except binascii.Error:
            pass
    return bytes(res)


def res_edit_out(res: Response, text: bytes) -> Response:
    """
    Encodes the content of the outgoing HTTP response using base64.

    Args:
        res: The outgoing HTTP response.
        text: The content to be base64-encoded.

    Returns:
        The HTTP response with the base64-encoded content.
    """
    if res.content:
        res.content = b64encode(text)
    return res
