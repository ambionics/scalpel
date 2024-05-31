"""
    Request Method Modification Script

    This script demonstrates modifying an incoming HTTP GET request to a POST request.
    It changes the content type to 'application/x-www-form-urlencoded' and transfers the
    query parameters to the URL-encoded form body.

    This is similar to the "Change request method" feature in Burp Suite.

    This is useful for testing purposes or scenarios where the server needs to handle the request differently.
"""

from typing import Optional
from pyscalpel import Request
from pyscalpel.http.body import URLEncodedForm


def request(req: Request) -> Optional[Request]:
    """
    Modifies an incoming GET request to a POST request and changes its content type.

    If the request method is GET, this function prints the request method and path,
    then changes the request method to POST, sets the content type to 'application/x-www-form-urlencoded',
    transfers the query parameters to the URL-encoded form body, and clears the query parameters.

    Args:
        req: The incoming HTTP request.

    Returns:
        The modified HTTP request if the method was GET, otherwise None.
    """
    print(req.method)
    if req.method == "GET":
        print(f"GET request to {req.path}")
        print("Changing request method")
        params = req.query
        req.method = "POST"
        req.content_type = "application/x-www-form-urlencoded"
        req.urlencoded_form = URLEncodedForm(params.items())
        req.query.clear()
        return req
