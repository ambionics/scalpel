from pyscalpel import Request, Response, Flow, MatchEvent


def match(flow: Flow, events: MatchEvent) -> bool:
    """- Determine whether an event should be handled by a hook.

    - Args:
        - flow ([Flow](../pdoc/python3-10/pyscalpel.html#Flow)): The event context (contains request and optional response).
        - events ([MatchEvent](../pdoc/python3-10/pyscalpel.html#MatchEvent)): The hook type (request, response, req_edit_in, ...).

    - Returns:
        - bool: True if the event must be handled. Otherwise, False.
    """


def request(req: Request) -> Request | None:
    """- Intercept and rewrite a request.

    - Args:
        - req ([Request](../pdoc/python3-10/pyscalpel.html#Request)): The intercepted request

    - Returns:
        - [Request](../pdoc/python3-10/pyscalpel.html#Request) or None: The modified request. Otherwise, None to ignore the request.
    """


def response(res: Response) -> Response | None:
    """- Intercept and rewrite a response.

    - Args:
        - res ([Response](../pdoc/python3-10/pyscalpel.html#Response)): The intercepted response.

    - Returns:
        - [Response](../pdoc/python3-10/pyscalpel.html#Response) or None: The modified response. Otherwise, None to ignore the response.
    """


def req_edit_in(req: Request) -> bytes | None:
    """- Create or update a request editor's content from a request.
       - May be used to decode a request to plaintext.

    - Args:
        - req ([Request](../pdoc/python3-10/pyscalpel.html#Request)): The HTTP request.

    - Returns:
        - bytes or None: The editor's contents.
    """


def req_edit_out(req: Request, modified_content: bytes) -> Request | None:
    """- Update a request from an editor's modified content.
       - May be used to encode a request from plaintext (modified_content).

    - Args:
        - req ([Request](../pdoc/python3-10/pyscalpel.html#Request)): The original request.
        - modified_content (bytes): The editor's content.

    - Returns:
        - [Request](../pdoc/python3-10/pyscalpel.html#Request) or None: The new request.
    """


def res_edit_in(res: Response) -> bytes | None:
    """- Create or update a response editor's content from a response.
       - May be used to decode a response to plaintext.

    - Args:
        - res ([Response](../pdoc/python3-10/pyscalpel.html#Response)): The HTTP response.

    - Returns:
        - bytes or None: The editor contents.
    """


def res_edit_out(res: Response, modified_content: bytes) -> Response | None:
    """- Update a response from an editor's modified content.
       - May be used to encode a response from plaintext (modified_content).

    - Args:
        - res ([Response](../pdoc/python3-10/pyscalpel.html#Response)): The original response.
        - modified_content (bytes): The editor's content.

    - Returns:
        - [Response](../pdoc/python3-10/pyscalpel.html#Response) or None: The new response.
    """
