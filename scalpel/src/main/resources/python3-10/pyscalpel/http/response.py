from __future__ import annotations

import time
from typing import Literal, cast
from _internal_mitmproxy.http import (
    Response as MITMProxyResponse,
)

from pyscalpel.java.burp.http_response import IHttpResponse, HttpResponse
from pyscalpel.burp_utils import get_bytes
from pyscalpel.java.burp.byte_array import IByteArray
from pyscalpel.java.scalpel_types.utils import PythonUtils
from pyscalpel.encoding import always_bytes
from pyscalpel.http.headers import Headers
from pyscalpel.http.utils import host_is
from pyscalpel.java.burp.http_service import IHttpService
from pyscalpel.java.burp.http_request import IHttpRequest
from pyscalpel.http.request import Request


class Response(MITMProxyResponse):
    """A "Burp oriented" HTTP response class


    This class allows to manipulate Burp responses in a Pythonic way.

    Fields:
        scheme: http or https
        host: The initiating request target host
        port: The initiating request target port
        request: The initiating request.
    """

    scheme: Literal["http", "https"] = "http"
    host: str = ""
    port: int = 0
    request: Request | None = None

    def __init__(
        self,
        http_version: bytes,
        status_code: int,
        reason: bytes,
        headers: Headers | tuple[tuple[bytes, bytes], ...],
        content: bytes | None,
        trailers: Headers | tuple[tuple[bytes, bytes], ...] | None,
        scheme: Literal["http", "https"] = "http",
        host: str = "",
        port: int = 0,
    ):
        # Construct the base/inherited MITMProxy response.
        super().__init__(
            http_version,
            status_code,
            reason,
            headers,
            content,
            trailers,
            timestamp_start=time.time(),
            timestamp_end=time.time(),
        )
        self.scheme = scheme
        self.host = host
        self.port = port

    @classmethod
    # https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response
    # link to mitmproxy documentation
    def from_mitmproxy(cls, response: MITMProxyResponse) -> Response:
        """Construct an instance of the Response class from a [mitmproxy.http.HTTPResponse](https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response).
        :param response: The [mitmproxy.http.HTTPResponse](https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response) to convert.
        :return: A :class:`Response` with the same data as the [mitmproxy.http.HTTPResponse](https://docs.mitmproxy.org/stable/api/mitmproxy/http.html#Response).
        """
        return cls(
            always_bytes(response.http_version),
            response.status_code,
            always_bytes(response.reason),
            Headers.from_mitmproxy(response.headers),
            response.content,
            Headers.from_mitmproxy(response.trailers) if response.trailers else None,
        )

    @classmethod
    def from_burp(
        cls,
        response: IHttpResponse,
        service: IHttpService | None = None,
        request: IHttpRequest | None = None,
    ) -> Response:
        """Construct an instance of the Response class from a Burp suite :class:`IHttpResponse`."""
        body = get_bytes(cast(IByteArray, response.body())) if response.body() else b""
        scalpel_response = cls(
            always_bytes(response.httpVersion() or "HTTP/1.1"),
            response.statusCode(),
            always_bytes(response.reasonPhrase() or b""),
            Headers.from_burp(response.headers()),
            body,
            None,
        )

        burp_request: IHttpRequest | None = request
        if burp_request is None:
            try:
                # Some responses can have a "initiatingRequest" field.
                # https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/http/handler/HttpResponseReceived.html#initiatingRequest():~:text=HttpRequest-,initiatingRequest(),-Returns%3A
                burp_request = response.initiatingRequest()  # type: ignore
            except AttributeError:
                pass

        if burp_request:
            scalpel_response.request = Request.from_burp(burp_request, service)

        if not service and burp_request:
            # The only way to check if the Java method exist without writing Java is catching the error.
            service = burp_request.httpService()

        if service:
            scalpel_response.scheme = "https" if service.secure() else "http"
            scalpel_response.host = service.host()
            scalpel_response.port = service.port()

        return scalpel_response

    def __bytes__(self) -> bytes:
        """Convert the response to raw bytes."""
        # Reserialize the response to bytes.

        # Format the first line of the response. (e.g. "HTTP/1.1 200 OK\r\n")
        first_line = (
            b" ".join(
                always_bytes(s)
                for s in (self.http_version, str(self.status_code), self.reason)
            )
            + b"\r\n"
        )

        # Format the response's headers part.
        headers_lines = b"".join(
            b"%s: %s\r\n" % (key, val) for key, val in self.headers.fields
        )

        # Set a default value for the response's body. (None -> b"")
        body = self.content or b""

        # Build the whole response and return it.
        return first_line + headers_lines + b"\r\n" + body

    def to_burp(self) -> IHttpResponse:  # pragma: no cover (uses Java API)
        """Convert the response to a Burp suite :class:`IHttpResponse`."""
        response_byte_array: IByteArray = PythonUtils.toByteArray(bytes(self))

        return HttpResponse.httpResponse(response_byte_array)

    @classmethod
    def from_raw(
        cls, data: bytes | str
    ) -> Response:  # pragma: no cover (uses Java API)
        """Construct an instance of the Response class from raw bytes.
        :param data: The raw bytes to convert.
        :return: A :class:`Response` parsed from the raw bytes.
        """
        # Use the Burp API to trivialize the parsing of the response from raw bytes.
        # Convert the raw bytes to a Burp ByteArray.
        # Plain strings are OK too.
        str_or_byte_array: IByteArray | str = (
            data if isinstance(data, str) else PythonUtils.toByteArray(data)
        )

        # Instantiate a new Burp HTTP response.
        burp_response: IHttpResponse = HttpResponse.httpResponse(str_or_byte_array)

        return cls.from_burp(burp_response)

    @classmethod
    def make(
        cls,
        status_code: int = 200,
        content: bytes | str = b"",
        headers: Headers | tuple[tuple[bytes, bytes], ...] = (),
        host: str = "",
        port: int = 0,
        scheme: Literal["http", "https"] = "http",
    ) -> "Response":
        # Use the base/inherited make method to construct a MITMProxy response.
        mitmproxy_res = MITMProxyResponse.make(status_code, content, headers)

        res = cls.from_mitmproxy(mitmproxy_res)
        res.host = host
        res.scheme = scheme
        res.port = port

        return res

    def host_is(self, *patterns: str) -> bool:
        """Matches the host against the provided patterns

        Returns:
            bool: Whether at least one pattern matched
        """
        return host_is(self.host, *patterns)

    @property
    def body(self) -> bytes | None:
        """Alias for content()

        Returns:
            bytes | None: The request body / content
        """
        return self.content

    @body.setter
    def body(self, val: bytes | None):
        self.content = val
