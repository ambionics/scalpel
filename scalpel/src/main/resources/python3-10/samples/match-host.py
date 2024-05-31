"""
    Host Matching 

    This example demonstrates the matching feature.
    
    It can be used to understand how to create matching rules to filter unwanted host from being processed.
    Here, we create a match hook which will only intercept requests to *.localhost and 127.0.0.1
"""

from pyscalpel import Request, Response, Flow


def match(flow: Flow) -> bool:
    """
    Matches the host of the HTTP request with the specified patterns.
    Will be called before calling other hooks to decide whether to ignore the event or not.

    Args:
        flow: The flow object representing the HTTP transaction.

    Returns:
        True if the host of the HTTP request matches either of the specified patterns, otherwise False.
    """
    return flow.host_is("*localhost", "127.0.0.1")


#### All of the hooks below will only be called if match() returns True ####


def request(req: Request) -> Request | None:
    """
    Intercepts and modifies the incoming HTTP request by adding a custom header.

    Args:
        req: The incoming HTTP request.

    Returns:
        The modified HTTP request.
    """
    req.headers["X-Python-Intercept-Request"] = "request"
    return req


def response(res: Response) -> Response | None:
    """
    Intercepts and modifies the incoming HTTP response by adding a custom header.

    Args:
        res: The incoming HTTP response.

    Returns:
        The modified HTTP response.
    """
    res.headers["X-Python-Intercept-Response"] = "response"
    return res


def req_edit_in(req: Request) -> bytes | None:
    """
    Modifies the incoming HTTP request before it is sent to the editor by adding a custom header.

    Args:
        req: The incoming HTTP request.

    Returns:
        The modified HTTP request as bytes.
    """
    req.headers["X-Python-In-Request-Editor"] = "req_edit_in"
    return bytes(req)


def req_edit_out(_: Request, text: bytes) -> Request | None:
    """
    Modifies the outgoing HTTP request after it has been edited by adding a custom header.

    Args:
        _: The original HTTP request (ignored).
        text: The edited HTTP request as bytes.

    Returns:
        The modified HTTP request.
    """
    req = Request.from_raw(text)
    req.headers["X-Python-Out-Request-Editor"] = "req_edit_out"
    return req


def res_edit_in(res: Response) -> bytes | None:
    """
    Modifies the incoming HTTP response before it is sent to the editor by adding a custom header.

    Args:
        res: The incoming HTTP response.

    Returns:
        The modified HTTP response as bytes.
    """
    res.headers["X-Python-In-Response-Editor"] = "res_edit_in"
    return bytes(res)


def res_edit_out(_: Response, text: bytes) -> Response | None:
    """
    Modifies the outgoing HTTP response after it has been edited by adding a custom header.

    Args:
        _: The original HTTP response (ignored).
        text: The edited HTTP response as bytes.

    Returns:
        The modified HTTP response.
    """
    res = Response.from_raw(text)
    res.headers["X-Python-Out-Response-Editor"] = "res_edit_out"
    return res
