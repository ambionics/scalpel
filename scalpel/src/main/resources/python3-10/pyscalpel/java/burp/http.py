from __future__ import annotations

# pylint: disable=invalid-name
# Stubs for https://portswigger.github.io/burp-extensions-montoya-api/javadoc/burp/api/montoya/http/Http.html
from abc import abstractmethod, ABCMeta
from typing import Protocol
from pyscalpel.java.object import JavaObject
from pyscalpel.java.burp import IHttpRequest, IHttpRequestResponse


class IHttp(JavaObject, Protocol, metaclass=ABCMeta):  # pragma: no cover
    """generated source for interface Http"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def sendRequest(self, request: IHttpRequest) -> IHttpRequestResponse:
        ...


# This class can only be instantiated with the API
