from __future__ import annotations

# pylint: disable=invalid-name

from abc import abstractmethod
from typing import overload, Protocol
from pyscalpel.java.burp.http_message import IHttpMessage
from pyscalpel.java.burp.byte_array import IByteArray
from pyscalpel.java.burp.http_header import IHttpHeader
from pyscalpel.java.object import JavaObject
from pyscalpel.java.import_java import import_java

#  * Burp HTTP response able to retrieve and modify details about an HTTP response.
#


class IHttpResponse(IHttpMessage, Protocol):  # pragma: no cover
    """generated source for interface HttpResponse"""

    #
    #      * Obtain the HTTP status code contained in the response.
    #      *
    #      * @return HTTP status code.
    #
    @abstractmethod
    def statusCode(self) -> int:
        """generated source for method statusCode"""

    #
    #      * Obtain the HTTP reason phrase contained in the response for HTTP 1 messages.
    #      * HTTP 2 messages will return a mapped phrase based on the status code.
    #      *
    #      * @return HTTP Reason phrase.
    #
    @abstractmethod
    def reasonPhrase(self) -> str | None:
        """generated source for method reasonPhrase"""

    #
    #      * Return the HTTP Version text parsed from the response line for HTTP 1 messages.
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
    #      * {@inheritDoc}
    #
    @abstractmethod
    def body(self) -> IByteArray | None:
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
    def markers(self) -> JavaObject:
        """generated source for method markers"""

    #
    #      * Obtain details of the HTTP cookies set in the response.
    #      *
    #      * @return A list of {@link Cookie} objects representing the cookies set in the response, if any.
    #
    @abstractmethod
    def cookies(self) -> JavaObject:
        """generated source for method cookies"""

    #
    #      * Obtain the MIME type of the response, as stated in the HTTP headers.
    #      *
    #      * @return The stated MIME type.
    #
    @abstractmethod
    def statedMimeType(self) -> JavaObject:
        """generated source for method statedMimeType"""

    #
    #      * Obtain the MIME type of the response, as inferred from the contents of the HTTP message body.
    #      *
    #      * @return The inferred MIME type.
    #
    @abstractmethod
    def inferredMimeType(self) -> JavaObject:
        """generated source for method inferredMimeType"""

    #
    #      * Retrieve the number of types given keywords appear in the response.
    #      *
    #      * @param keywords Keywords to count.
    #      *
    #      * @return List of keyword counts in the order they were provided.
    #
    @abstractmethod
    def keywordCounts(self, *keywords) -> int:
        """generated source for method keywordCounts"""

    #
    #      * Retrieve the values of response attributes.
    #      *
    #      * @param types Response attributes to retrieve values for.
    #      *
    #      * @return List of {@link Attribute} objects.
    #
    @abstractmethod
    def attributes(self, *types) -> JavaObject:
        """generated source for method attributes"""

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
    #      * Create a copy of the {@code HttpResponse} in temporary file.<br>
    #      * This method is used to save the {@code HttpResponse} object to a temporary file,
    #      * so that it is no longer held in memory. Extensions can use this method to convert
    #      * {@code HttpResponse} objects into a form suitable for long-term usage.
    #      *
    #      * @return A new {@code HttpResponse} instance stored in temporary file.
    #
    @abstractmethod
    def copyToTempFile(self) -> IHttpResponse:
        """generated source for method copyToTempFile"""

    #
    #      * Create a copy of the {@code HttpResponse} with the provided status code.
    #      *
    #      * @param statusCode the new status code for response
    #      *
    #      * @return A new {@code HttpResponse} instance.
    #
    @abstractmethod
    def withStatusCode(self, statusCode: int) -> IHttpResponse:
        """generated source for method withStatusCode"""

    #
    #      * Create a copy of the {@code HttpResponse} with the new reason phrase.
    #      *
    #      * @param reasonPhrase the new reason phrase for response
    #      *
    #      * @return A new {@code HttpResponse} instance.
    #
    @abstractmethod
    def withReasonPhrase(self, reasonPhrase: str) -> IHttpResponse:
        """generated source for method withReasonPhrase"""

    #
    #      * Create a copy of the {@code HttpResponse} with the new http version.
    #      *
    #      * @param httpVersion the new http version for response
    #      *
    #      * @return A new {@code HttpResponse} instance.
    #
    @abstractmethod
    def withHttpVersion(self, httpVersion: str) -> IHttpResponse:
        """generated source for method withHttpVersion"""

    #
    #      * Create a copy of the {@code HttpResponse} with the updated body.<br>
    #      * Updates Content-Length header.
    #      *
    #      * @param body the new body for the response
    #      *
    #      * @return A new {@code HttpResponse} instance.
    #
    @abstractmethod
    def withBody(self, body: IByteArray | str) -> IHttpResponse:
        """generated source for method withBody"""

    #
    #      * Create a copy of the {@code HttpResponse} with the added header.
    #      *
    #      * @param header The {@link HttpHeader} to add to the response.
    #      *
    #      * @return The updated response containing the added header.
    #
    # @abstractmethod
    # def withAddedHeader(self, header) -> 'IHttpResponse':
    #     """ generated source for method withAddedHeader """

    # #
    # #      * Create a copy of the {@code HttpResponse}  with the added header.
    # #      *
    # #      * @param name  The name of the header.
    # #      * @param value The value of the header.
    # #      *
    # #      * @return The updated response containing the added header.
    # #
    @abstractmethod
    def withAddedHeader(self, name: str, value: str) -> IHttpResponse:
        """generated source for method withAddedHeader_0"""

    #
    #      * Create a copy of the {@code HttpResponse}  with the updated header.
    #      *
    #      * @param header The {@link HttpHeader} to update containing the new value.
    #      *
    #      * @return The updated response containing the updated header.
    #
    # @abstractmethod
    # def withUpdatedHeader(self, header) -> 'IHttpResponse':
    #     """ generated source for method withUpdatedHeader """

    # #
    # #      * Create a copy of the {@code HttpResponse}  with the updated header.
    # #      *
    # #      * @param name  The name of the header to update the value of.
    # #      * @param value The new value of the specified HTTP header.
    # #      *
    # #      * @return The updated response containing the updated header.
    # #
    @abstractmethod
    def withUpdatedHeader(self, name: str, value: str) -> IHttpResponse:
        """generated source for method withUpdatedHeader_0"""

    #
    #      * Create a copy of the {@code HttpResponse}  with the removed header.
    #      *
    #      * @param header The {@link HttpHeader} to remove from the response.
    #      *
    #      * @return The updated response containing the removed header.
    #
    # @abstractmethod
    # def withRemovedHeader(self, header) -> 'IHttpResponse':
    #     """ generated source for method withRemovedHeader """

    # #
    # #      * Create a copy of the {@code HttpResponse}  with the removed header.
    # #      *
    # #      * @param name The name of the HTTP header to remove from the response.
    # #      *
    # #      * @return The updated response containing the removed header.
    # #
    @abstractmethod
    def withRemovedHeader(self, name: str) -> IHttpResponse:
        """generated source for method withRemovedHeader_0"""

    #
    #      * Create a copy of the {@code HttpResponse} with the added markers.
    #      *
    #      * @param markers Request markers to add.
    #      *
    #      * @return A new {@code MarkedHttpRequestResponse} instance.
    #
    @abstractmethod
    @overload
    def withMarkers(self, markers: JavaObject) -> IHttpResponse:
        """generated source for method withMarkers"""

    #
    #      * Create a copy of the {@code HttpResponse} with the added markers.
    #      *
    #      * @param markers Request markers to add.
    #      *
    #      * @return A new {@code MarkedHttpRequestResponse} instance.
    #
    @abstractmethod
    @overload
    def withMarkers(self, *markers: JavaObject) -> IHttpResponse:
        """generated source for method withMarkers_0"""

    #
    #      * Create a new empty instance of {@link HttpResponse}.<br>
    #      *
    #      * @return A new {@link HttpResponse} instance.
    #
    @abstractmethod
    def httpResponse(self, response: IByteArray | str) -> IHttpResponse:
        """generated source for method httpResponse"""


HttpResponse: IHttpResponse = import_java(
    "burp.api.montoya.http.message.responses", "HttpResponse", IHttpResponse
)
