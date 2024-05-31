from __future__ import annotations

# pylint: disable=invalid-name
#
#  * Burp HTTP parameter able to retrieve to hold details about an HTTP request parameter.
#


from abc import ABCMeta, abstractmethod
from pyscalpel.java.object import JavaObject
from pyscalpel.java.import_java import import_java


class IHttpParameter(JavaObject):  # pragma: no cover
    """generated source for interface HttpParameter"""

    __metaclass__ = ABCMeta
    #
    #      * @return The parameter type.
    #

    @abstractmethod
    def type_(self) -> JavaObject:
        """generated source for method type_"""

    #
    #      * @return The parameter name.
    #
    @abstractmethod
    def name(self) -> str:
        """generated source for method name"""

    #
    #      * @return The parameter value.
    #
    @abstractmethod
    def value(self) -> str:
        """generated source for method value"""

    #
    #      * Create a new Instance of {@code HttpParameter} with {@link HttpParameterType#URL} type.
    #      *
    #      * @param name  The parameter name.
    #      * @param value The parameter value.
    #      *
    #      * @return A new {@code HttpParameter} instance.
    #
    @abstractmethod
    def urlParameter(self, name: str, value: str) -> IHttpParameter:
        """generated source for method urlParameter"""

    #
    #      * Create a new Instance of {@code HttpParameter} with {@link HttpParameterType#BODY} type.
    #      *
    #      * @param name  The parameter name.
    #      * @param value The parameter value.
    #      *
    #      * @return A new {@code HttpParameter} instance.
    #
    @abstractmethod
    def bodyParameter(self, name: str, value: str) -> IHttpParameter:
        """generated source for method bodyParameter"""

    #
    #      * Create a new Instance of {@code HttpParameter} with {@link HttpParameterType#COOKIE} type.
    #      *
    #      * @param name  The parameter name.
    #      * @param value The parameter value.
    #      *
    #      * @return A new {@code HttpParameter} instance.
    #
    @abstractmethod
    def cookieParameter(self, name: str, value: str) -> IHttpParameter:
        """generated source for method cookieParameter"""

    #
    #      * Create a new Instance of {@code HttpParameter} with the specified type.
    #      *
    #      * @param name  The parameter name.
    #      * @param value The parameter value.
    #      * @param type  The header type.
    #      *
    #      * @return A new {@code HttpParameter} instance.
    #
    @abstractmethod
    def parameter(self, name: str, value: str, type_: JavaObject) -> IHttpParameter:
        """generated source for method parameter"""


# from burp.api.montoya.http.message.params import (  # pylint: disable=import-error # type: ignore
#     HttpParameter as _BurpHttpParameter,
# )

# HttpParameter: IHttpParameter = _BurpHttpParameter

HttpParameter: IHttpParameter = import_java(
    "burp.api.montoya.http.message.params", "HttpParameter", IHttpParameter
)
