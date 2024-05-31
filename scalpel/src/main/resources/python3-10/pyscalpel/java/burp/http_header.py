from __future__ import annotations

# pylint: disable=invalid-name
#
#  * Burp HTTP header able to retrieve to hold details about an HTTP header.
#


from abc import abstractmethod, ABCMeta
from typing import overload, Protocol
from pyscalpel.java.object import JavaObject
from pyscalpel.java.import_java import import_java


class IHttpHeader(JavaObject, Protocol, metaclass=ABCMeta):  # pragma: no cover
    """generated source for interface HttpHeader"""

    __metaclass__ = ABCMeta
    #
    #      * @return The name of the header.
    #

    @abstractmethod
    def name(self) -> str:
        """generated source for method name"""

    #
    #      * @return The value of the header.
    #
    @abstractmethod
    def value(self) -> str:
        """generated source for method value"""

    #
    #      * @return The {@code String} representation of the header.
    #
    @abstractmethod
    def __str__(self):
        """generated source for method toString"""

    #
    #      * Create a new instance of {@code HttpHeader} from name and value.
    #      *
    #      * @param name  The name of the header.
    #      * @param value The value of the header.
    #      *
    #      * @return A new {@code HttpHeader} instance.
    #
    @abstractmethod
    @overload
    def httpHeader(self, name: str, value: str) -> IHttpHeader:
        """generated source for method httpHeader"""

    #
    #      * Create a new instance of HttpHeader from a {@code String} header representation.
    #      * It will be parsed according to the HTTP/1.1 specification for headers.
    #      *
    #      * @param header The {@code String} header representation.
    #      *
    #      * @return A new {@code HttpHeader} instance.
    #
    @abstractmethod
    @overload
    def httpHeader(self, header: str) -> IHttpHeader:
        """generated source for method httpHeader_0"""


HttpHeader: IHttpHeader = import_java(
    "burp.api.montoya.http.message", "HttpHeader", IHttpHeader
)
