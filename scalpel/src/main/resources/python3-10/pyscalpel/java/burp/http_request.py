from __future__ import annotations

# pylint: disable=invalid-name

from abc import abstractmethod
from typing import Iterable, Protocol, overload
from pyscalpel.java.burp.byte_array import IByteArray
from pyscalpel.java.burp.http_header import IHttpHeader
from pyscalpel.java.burp.http_message import IHttpMessage
from pyscalpel.java.burp.http_parameter import IHttpParameter
from pyscalpel.java.burp.http_service import IHttpService
from pyscalpel.java.object import JavaObject
from pyscalpel.java.import_java import import_java

#  * Burp HTTP request able to retrieve and modify details of an HTTP request.
#


class IHttpRequest(IHttpMessage, Protocol):  # pragma: no cover
    """generated source for interface HttpRequest"""

    #      * HTTP service for the request.
    #      *
    #      * @return An {@link HttpService} object containing details of the HTTP service.
    #

    @abstractmethod
    def httpService(self) -> IHttpService:
        """generated source for method httpService"""

    #
    #      * URL for the request.
    #      * If the request is malformed, then a {@link MalformedRequestException} is thrown.
    #      *
    #      * @return The URL in the request.
    #      * @throws MalformedRequestException if request is malformed.
    #

    @abstractmethod
    def url(self) -> str:
        """generated source for method url"""

    #
    #      * HTTP method for the request.
    #      * If the request is malformed, then a {@link MalformedRequestException} is thrown.
    #      *
    #      * @return The HTTP method used in the request.
    #      * @throws MalformedRequestException if request is malformed.
    #

    @abstractmethod
    def method(self) -> str:
        """generated source for method method"""

    #
    #      * Path and File for the request.
    #      * If the request is malformed, then a {@link MalformedRequestException} is thrown.
    #      *
    #      * @return the path and file in the request
    #      * @throws MalformedRequestException if request is malformed.
    #

    @abstractmethod
    def path(self) -> str:
        """generated source for method path"""

    #
    #      * HTTP Version text parsed from the request line for HTTP 1 messages.
    #      * HTTP 2 messages will return "HTTP/2"
    #      *
    #      * @return Version string
    #

    @abstractmethod
    def httpVersion(self) -> str | None:
        """generated source for method httpVersion"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def headers(self) -> list[IHttpHeader]:
        """generated source for method headers"""

    #
    #      * @return The detected content type of the request.
    #

    @abstractmethod
    def contentType(self) -> JavaObject:
        """generated source for method contentType"""

    #
    #      * @return The parameters contained in the request.
    #

    @abstractmethod
    def parameters(self) -> list[IHttpParameter]:
        """generated source for method parameters"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def body(self) -> IByteArray:
        """generated source for method body"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def bodyToString(self) -> str:
        """generated source for method bodyToString"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def bodyOffset(self) -> int:
        """generated source for method bodyOffset"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def markers(self):
        """generated source for method markers"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def toByteArray(self) -> IByteArray:
        """generated source for method toByteArray"""

    #
    #      * {@inheritDoc}
    #

    @abstractmethod
    def __str__(self) -> str:
        """generated source for method toString"""

    #
    #      * Create a copy of the {@code HttpRequest} in temporary file.<br>
    #      * This method is used to save the {@code HttpRequest} object to a temporary file,
    #      * so that it is no longer held in memory. Extensions can use this method to convert
    #      * {@code HttpRequest} objects into a form suitable for long-term usage.
    #      *
    #      * @return A new {@code ByteArray} instance stored in temporary file.
    #

    @abstractmethod
    def copyToTempFile(self) -> IHttpRequest:
        """generated source for method copyToTempFile"""

    #
    #      * Create a copy of the {@code HttpRequest} with the new service.
    #      *
    #      * @param service An {@link HttpService} reference to add.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withService(self, service: IHttpService) -> IHttpRequest:
        """generated source for method withService"""

    #
    #      * Create a copy of the {@code HttpRequest} with the new path.
    #      *
    #      * @param path The path to use.
    #      *
    #      * @return A new {@code HttpRequest} instance with updated path.
    #

    @abstractmethod
    def withPath(self, path: str) -> IHttpRequest:
        """generated source for method withPath"""

    #
    #      * Create a copy of the {@code HttpRequest} with the new method.
    #      *
    #      * @param method the method to use
    #      *
    #      * @return a new {@code HttpRequest} instance with updated method.
    #

    @abstractmethod
    def withMethod(self, method: str) -> IHttpRequest:
        """generated source for method withMethod"""

    #
    #      * Create a copy of the {@code HttpRequest} with the added HTTP parameters.
    #      *
    #      * @param parameters HTTP parameters to add.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withAddedParameters(self, parameters: Iterable[IHttpParameter]) -> IHttpRequest:
        """generated source for method withAddedParameters"""

    #
    #      * Create a copy of the {@code HttpRequest} with the added HTTP parameters.
    #      *
    #      * @param parameters HTTP parameters to add.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withAddedParameters_0(self, *parameters: IHttpParameter) -> IHttpRequest:
        """generated source for method withAddedParameters_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with the removed HTTP parameters.
    #      *
    #      * @param parameters HTTP parameters to remove.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withRemovedParameters(
        self, parameters: Iterable[IHttpParameter]
    ) -> IHttpRequest:
        """generated source for method withRemovedParameters"""

    #
    #      * Create a copy of the {@code HttpRequest} with the removed HTTP parameters.
    #      *
    #      * @param parameters HTTP parameters to remove.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withRemovedParameters_0(self, *parameters: IHttpParameter) -> IHttpRequest:
        """generated source for method withRemovedParameters_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with the updated HTTP parameters.<br>
    #      * If a parameter does not exist in the request, a new one will be added.
    #      *
    #      * @param parameters HTTP parameters to update.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withUpdatedParameters(self, parameters: list[IHttpParameter]) -> IHttpRequest:
        """generated source for method withUpdatedParameters"""

    #
    #      * Create a copy of the {@code HttpRequest} with the updated HTTP parameters.<br>
    #      * If a parameter does not exist in the request, a new one will be added.
    #      *
    #      * @param parameters HTTP parameters to update.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withUpdatedParameters_0(self, *parameters: IHttpParameter) -> IHttpRequest:
        """generated source for method withUpdatedParameters_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with the transformation applied.
    #      *
    #      * @param transformation Transformation to apply.
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withTransformationApplied(self, transformation) -> IHttpRequest:
        """generated source for method withTransformationApplied"""

    #
    #      * Create a copy of the {@code HttpRequest} with the updated body.<br>
    #      * Updates Content-Length header.
    #      *
    #      * @param body the new body for the request
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withBody(self, body) -> IHttpRequest:
        """generated source for method withBody"""

    #
    #      * Create a copy of the {@code HttpRequest} with the updated body.<br>
    #      * Updates Content-Length header.
    #      *
    #      * @param body the new body for the request
    #      *
    #      * @return A new {@code HttpRequest} instance.
    #

    @abstractmethod
    def withBody_0(self, body: IByteArray) -> IHttpRequest:
        """generated source for method withBody_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with the added header.
    #      *
    #      * @param name  The name of the header.
    #      * @param value The value of the header.
    #      *
    #      * @return The updated HTTP request with the added header.
    #

    @abstractmethod
    def withAddedHeader(self, name: str, value: str) -> IHttpRequest:
        """generated source for method withAddedHeader"""

    #
    #      * Create a copy of the {@code HttpRequest} with the added header.
    #      *
    #      * @param header The {@link HttpHeader} to add to the HTTP request.
    #      *
    #      * @return The updated HTTP request with the added header.
    #

    @abstractmethod
    def withAddedHeader_0(self, header: IHttpHeader) -> IHttpRequest:
        """generated source for method withAddedHeader_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with the updated header.
    #      *
    #      * @param name  The name of the header to update the value of.
    #      * @param value The new value of the specified HTTP header.
    #      *
    #      * @return The updated request containing the updated header.
    #

    @abstractmethod
    def withUpdatedHeader(self, name: str, value: str) -> IHttpRequest:
        """generated source for method withUpdatedHeader"""

    #
    #      * Create a copy of the {@code HttpRequest} with the updated header.
    #      *
    #      * @param header The {@link HttpHeader} to update containing the new value.
    #      *
    #      * @return The updated request containing the updated header.
    #

    @abstractmethod
    def withUpdatedHeader_0(self, header: IHttpHeader) -> IHttpRequest:
        """generated source for method withUpdatedHeader_0"""

    #
    #      * Removes an existing HTTP header from the current request.
    #      *
    #      * @param name The name of the HTTP header to remove from the request.
    #      *
    #      * @return The updated request containing the removed header.
    #

    @abstractmethod
    def withRemovedHeader(self, name: str) -> IHttpRequest:
        """generated source for method withRemovedHeader"""

    #
    #      * Removes an existing HTTP header from the current request.
    #      *
    #      * @param header The {@link HttpHeader} to remove from the request.
    #      *
    #      * @return The updated request containing the removed header.
    #

    @abstractmethod
    def withRemovedHeader_0(self, header: IHttpHeader) -> IHttpRequest:
        """generated source for method withRemovedHeader_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with the added markers.
    #      *
    #      * @param markers Request markers to add.
    #      *
    #      * @return A new {@code MarkedHttpRequestResponse} instance.
    #

    @abstractmethod
    def withMarkers(self, markers) -> IHttpRequest:
        """generated source for method withMarkers"""

    #
    #      * Create a copy of the {@code HttpRequest} with the added markers.
    #      *
    #      * @param markers Request markers to add.
    #      *
    #      * @return A new {@code MarkedHttpRequestResponse} instance.
    #

    @abstractmethod
    def withMarkers_0(self, *markers) -> IHttpRequest:
        """generated source for method withMarkers_0"""

    #
    #      * Create a copy of the {@code HttpRequest} with added default headers.
    #      *
    #      * @return a new (@code HttpRequest) with added default headers
    #

    @abstractmethod
    def withDefaultHeaders(self) -> IHttpRequest:
        """generated source for method withDefaultHeaders"""

    #
    #      * Create a new empty instance of {@link HttpRequest}.<br>
    #      *
    #      * @².
    #

    @abstractmethod
    @overload
    def httpRequest(self, request: IByteArray | str) -> IHttpRequest:
        """generated source for method httpRequest"""

    @abstractmethod
    @overload
    def httpRequest(self, service: IHttpService, req: IByteArray | str) -> IHttpRequest:
        """generated source for method httpRequest"""

    #
    #      * Create a new instance of {@link HttpRequest}.<br>
    #      *
    #      *
    #      * @².
    #
    #

    @abstractmethod
    def httpRequestFromUrl(self, url: str) -> IHttpRequest:
        """generated source for method httpRequestFromUrl"""

    #
    #      * Create a new instance of {@link HttpRequest} containing HTTP 2 headers and body.<br>
    #      *
    #      * @param service An HTTP service for the request.
    #      * @param headers A list of HTTP 2 headers.
    #      * @param body    A body of the HTTP 2 request.
    #      *
    #      * @².
    #

    @abstractmethod
    def http2Request(
        self, service: IHttpService, headers: Iterable[IHttpHeader], body: IByteArray
    ) -> IHttpRequest:
        """generated source for method http2Request"""

    #
    #      * Create a new instance of {@link HttpRequest} containing HTTP 2 headers and body.<br>
    #      *
    #      * @param service An HTTP service for the request.
    #      * @param headers A list of HTTP 2 headers.
    #      * @param body    A body of the HTTP 2 request.
    #      *
    #      * @².
    #


# if "pdoc" in modules:
#     _BurpHttpRequest = cast(IHttpRequest, None)
# else:
#     try:
#         from burp.api.montoya.http.message.requests import (  # pylint: disable=import-error # type: ignore
#             HttpRequest as _BurpHttpRequest,
#         )
#     except ImportError as exc:
#         raise ImportError("Could not import Java class HttpRequest") from exc

# HttpRequest = _BurpHttpRequest
HttpRequest: IHttpRequest = import_java(
    "burp.api.montoya.http.message.requests", "HttpRequest", IHttpRequest
)
