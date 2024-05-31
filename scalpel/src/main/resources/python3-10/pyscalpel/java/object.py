from __future__ import annotations

# pylint: disable=invalid-name

from abc import abstractmethod, ABCMeta
from typing import overload, Protocol


class JavaObject(Protocol, metaclass=ABCMeta):
    """generated source for class Object"""

    @abstractmethod
    def __init__(self):
        """generated source for method __init__"""

    @abstractmethod
    def getClass(self) -> JavaClass:
        """generated source for method getClass"""

    @abstractmethod
    def hashCode(self) -> int:
        """generated source for method hashCode"""

    @abstractmethod
    def equals(self, obj) -> bool:
        """generated source for method equals"""

    @abstractmethod
    def clone(self) -> JavaObject:
        """generated source for method clone"""

    @abstractmethod
    def __str__(self) -> str:
        """generated source for method toString"""

    @abstractmethod
    def notify(self) -> None:
        """generated source for method notify"""

    @abstractmethod
    def notifyAll(self) -> None:
        """generated source for method notifyAll"""

    @abstractmethod
    @overload
    def wait(self) -> None:
        """generated source for method wait"""

    @abstractmethod
    @overload
    def wait(self, arg0: int) -> None:
        """generated source for method wait_0"""

    @abstractmethod
    @overload
    def wait(self, timeoutMillis: int, nanos: int) -> None:
        """generated source for method wait_1"""

    @abstractmethod
    def finalize(self) -> None:
        """generated source for method finalize"""


class JavaClass(JavaObject, metaclass=ABCMeta):
    pass
