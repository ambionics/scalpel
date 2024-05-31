"""
    Parameter Manipulation

    This example provides utility functions to manipulate HTTP request query parameters.
    It decodes and encodes parameter values, and gets and sets values for parameters with names derived from a "tab name".
    This is useful in HTTP request manipulation in applications such as proxies, web scrapers, and web services.
"""

from pyscalpel import Request
from pyscalpel.utils import (
    urldecode,
    urlencode_all,
    get_tab_name,
)


def get_and_decode_param(req: Request, param: str) -> bytes | None:
    """
    Retrieves the value of the specified query parameter from the given request, and URL-decodes it.

    Args:
        req: The request from which to retrieve the query parameter.
        param: The name of the query parameter to retrieve and decode.

    Returns:
        The URL-decoded value of the query parameter, or None if the parameter is not found.
    """
    found = req.query.get(param)
    if found is not None:
        return urldecode(found)


def set_and_encode_param(req: Request, param: str, param_value: bytes) -> Request:
    """
    URL-encodes the given value and sets it as the value of the specified query parameter in the given request.

    Args:
        req: The request in which to set the query parameter.
        param: The name of the query parameter to set.
        param_value: The value to URL-encode and set for the query parameter.

    Returns:
        The updated request with the encoded query parameter set.
    """
    req.query[param] = urlencode_all(param_value)
    return req


def req_edit_in_filename(req: Request) -> bytes | None:
    """
    Retrieves the filename from the request's query parameters.

    Args:
        req: The request from which to retrieve the filename.

    Returns:
        The URL-decoded filename, or None if the parameter is not found.
    """
    return get_and_decode_param(req, get_tab_name())


def req_edit_out_filename(req: Request, text: bytes) -> Request | None:
    """
    Sets the filename in the request's query parameters.

    Args:
        req: The request in which to set the filename.
        text: The filename to URL-encode and set.

    Returns:
        The updated request with the encoded filename set.
    """
    return set_and_encode_param(req, get_tab_name(), text)


def req_edit_in_directory(req: Request) -> bytes | None:
    """
    Retrieves the directory from the request's query parameters.

    Args:
        req: The request from which to retrieve the directory.

    Returns:
        The URL-decoded directory, or None if the parameter is not found.
    """
    return get_and_decode_param(req, get_tab_name())


def req_edit_out_directory(req: Request, text: bytes) -> Request | None:
    """
    Sets the directory in the request's query parameters.

    Args:
        req: The request in which to set the directory.
        text: The directory to URL-encode and set.

    Returns:
        The updated request with the encoded directory set.
    """
    return set_and_encode_param(req, get_tab_name(), text)
