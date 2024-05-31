"""
    Default script

    This script demonstrates basic usage of Scalpel by adding debug headers to HTTP requests and responses.
    It shows how to intercept and modify HTTP traffic using custom headers, and how to create editors using req_edit_* / res_edit_* hooks.
"""

from pyscalpel import Request, Response


def request(req: Request) -> Request | None:
    """
    Adds a debug header to every outgoing HTTP request.

    Args:
        req: The outgoing HTTP request.

    Returns:
        The modified HTTP request with the debug header.
    """
    req.headers["X-Python-Intercept-Request"] = "request"
    return req


def response(res: Response) -> Response | None:
    """
    Adds a debug header to every incoming HTTP response.

    Args:
        res: The incoming HTTP response.

    Returns:
        The modified HTTP response with the debug header.
    """
    res.headers["X-Python-Intercept-Response"] = "response"
    return res


def req_edit_in(req: Request) -> bytes | None:
    """
    Converts a request to the text to display in the editor and adds a debug header.

    Args:
        req: The incoming HTTP request.

    Returns:
        The modified request as bytes with the debug header.
    """
    req.headers["X-Python-In-Request-Editor"] = "req_edit_in"
    return bytes(req)


def req_edit_out(_: Request, text: bytes) -> Request | None:
    """
    Converts the modified editor text back to a request and adds a debug header.

    Args:
        _: The original HTTP request (unused).
        text: The request content as bytes.

    Returns:
        The modified HTTP request with the debug header.
    """
    req = Request.from_raw(text)
    req.headers["X-Python-Out-Request-Editor"] = "req_edit_out"
    return req


def res_edit_in(res: Response) -> bytes | None:
    """
    Converts a response to the text to display in the editor and adds a debug header.

    Args:
        res: The incoming HTTP response.

    Returns:
        The modified response as bytes with the debug header.
    """
    res.headers["X-Python-In-Response-Editor"] = "res_edit_in"
    return bytes(res)


def res_edit_out(_: Response, text: bytes) -> Response | None:
    """
    Converts the modified editor text back to a response and adds a debug header.

    Args:
        _: The original HTTP response (unused).
        text: The response content as bytes.

    Returns:
        The modified HTTP response with the debug header.
    """
    res = Response.from_raw(text)
    res.headers["X-Python-Out-Response-Editor"] = "res_edit_out"
    return res
