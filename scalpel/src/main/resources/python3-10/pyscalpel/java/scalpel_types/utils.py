# pylint: disable=invalid-name

from typing import TypeVar
from abc import ABCMeta, abstractmethod
from pyscalpel.java.object import JavaObject
from pyscalpel.java.bytes import JavaBytes
from pyscalpel.java.burp.http_request import IHttpRequest
from pyscalpel.java.burp.http_response import IHttpResponse
from pyscalpel.java.burp.byte_array import IByteArray
from pyscalpel.java.import_java import import_java

RequestOrResponse = TypeVar("RequestOrResponse", bound=IHttpRequest | IHttpResponse)


class IPythonUtils(JavaObject):  # pragma: no cover
    __metaclass__ = ABCMeta

    @abstractmethod
    def toPythonBytes(self, java_bytes: JavaBytes) -> list[int]:
        pass

    @abstractmethod
    def toJavaBytes(self, python_bytes: bytes | list[int] | bytearray) -> JavaBytes:
        pass

    @abstractmethod
    def toByteArray(self, python_bytes: bytes | list[int] | bytearray) -> IByteArray:
        pass

    @abstractmethod
    def getClassName(self, msg: JavaObject) -> str:
        pass

    @abstractmethod
    def updateHeader(
        self, msg: RequestOrResponse, name: str, value: str
    ) -> RequestOrResponse:
        pass


PythonUtils: IPythonUtils = import_java("lexfo.scalpel", "PythonUtils", IPythonUtils)
