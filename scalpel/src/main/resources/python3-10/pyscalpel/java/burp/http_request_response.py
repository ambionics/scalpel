from __future__ import annotations

# pylint: disable=invalid-name
# Stubs for https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/http/message/HttpRequestResponse.html
from abc import abstractmethod, ABCMeta
from typing import Protocol
from pyscalpel.java.object import JavaObject
from pyscalpel.java.burp import IHttpRequest, IHttpResponse


class IHttpRequestResponse(JavaObject, Protocol, metaclass=ABCMeta):  # pragma: no cover
    """generated source for interface HttpRequestResponse"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def request(self) -> IHttpRequest | None:
        ...

    @abstractmethod
    def response(self) -> IHttpResponse | None:
        ...
