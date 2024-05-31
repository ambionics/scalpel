# pylint: disable=invalid-name

from abc import abstractmethod
from typing import Protocol
from pyscalpel.java.burp.byte_array import IByteArray
from pyscalpel.java.burp.http_header import IHttpHeader
from pyscalpel.java.object import JavaObject

#
#  * Burp message retrieve common information shared by {@link HttpRequest} and {@link HttpResponse}.
#


class IHttpMessage(JavaObject, Protocol):  # pragma: no cover
    """generated source for interface HttpMessage"""

    #
    #      * HTTP headers contained in the message.
    #      *
    #      * @return A list of HTTP headers.
    #
    @abstractmethod
    def headers(self) -> IHttpHeader:
        """generated source for method headers"""

    #
    #      * Offset within the message where the message body begins.
    #      *
    #      * @return The message body offset.
    #
    @abstractmethod
    def bodyOffset(self) -> int:
        """generated source for method bodyOffset"""

    #
    #      * Body of a message as a byte array.
    #      *
    #      * @return The body of a message as a byte array.
    #
    @abstractmethod
    def body(self) -> IByteArray:
        """generated source for method body"""

    #
    #      * Body of a message as a {@code String}.
    #      *
    #      * @return The body of a message as a {@code String}.
    #
    @abstractmethod
    def bodyToString(self) -> str:
        """generated source for method bodyToString"""

    #
    #      * Markers for the message.
    #      *
    #      * @return A list of markers.
    #
    @abstractmethod
    def markers(self) -> JavaObject:
        """generated source for method markers"""

    #
    #      * Message as a byte array.
    #      *
    #      * @return The message as a byte array.
    #
    @abstractmethod
    def toByteArray(self) -> IByteArray:
        """generated source for method toByteArray"""

    #
    #      * Message as a {@code String}.
    #      *
    #      * @return The message as a {@code String}.
    #
    @abstractmethod
    def __str__(self) -> str:
        """generated source for method toString"""
