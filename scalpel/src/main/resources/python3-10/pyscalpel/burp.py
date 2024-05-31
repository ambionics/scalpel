from pyscalpel import Request, ctx
from threading import Thread


def send_to_repeater(
    req: Request, title: str | None = None
) -> None:  # pragma: no cover
    """Sends an HTTP request to the Burp Repeater tool.

    The request will be displayed in the user interface using a default tab index, but will not be sent until the user initiates this action.

    Args:
        req (Request): The full HTTP request.

        title (str | None, optional): An optional caption which will appear on the Repeater tab containing the request.
        If this value is None then a default tab index will be displayed.
    """
    # Convert request to Burp format.
    breq = req.to_burp()

    # Directly access the Montoya API Java object to send the request to repeater
    repeater = ctx["API"].repeater()

    # waiting for sendToRepeater while intercepting a request causes a Burp deadlock
    if title is None:
        Thread(target=lambda: repeater.sendToRepeater(breq)).start()
    else:
        # https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/repeater/Repeater.html#sendToRepeater(burp.api.montoya.http.message.requests.HttpRequest)
        Thread(target=lambda: repeater.sendToRepeater(breq, title)).start()
