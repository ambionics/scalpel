from __future__ import annotations

from typing import Protocol, TypeVar
from abc import ABC, abstractmethod, ABCMeta

from collections.abc import MutableMapping

from pyscalpel.http.headers import Headers


class ObjectWithHeadersField(Protocol):
    headers: Headers


class ObjectWithHeadersProperty(Protocol):
    @property
    def headers(self) -> Headers: ...

    @headers.setter
    def headers(self, value): ...


# Multipart needs the Content-Type header for the boundary parameter
# So Serializer needs an object that references the header
# This is used as a Forward declaration
ObjectWithHeaders = ObjectWithHeadersField | ObjectWithHeadersProperty

KT = TypeVar("KT")
VT = TypeVar("VT")


class Form(MutableMapping[KT, VT], metaclass=ABCMeta):
    pass


Scalars = str | bytes | int | bool | float

TupleExportedForm = tuple[
    tuple[bytes, bytes | None],
    ...,
]


ExportedForm = TupleExportedForm


# Abstract base class
class FormSerializer(ABC):
    @abstractmethod
    def serialize(self, deserialized_body: Form, req: ObjectWithHeaders) -> bytes:
        """Serialize a parsed form to raw bytes

        Args:
            deserialized_body (Form): The parsed form
            req (ObjectWithHeaders): The originating request (used for multipart to get an up to date boundary from content-type)

        Returns:
            bytes: Form's raw bytes representation
        """

    @abstractmethod
    def deserialize(self, body: bytes, req: ObjectWithHeaders) -> Form | None:
        """Parses the form from its raw bytes representation

        Args:
            body (bytes): The form as bytes
            req (ObjectWithHeaders): The originating request  (used for multipart to get an up to date boundary from content-type)

        Returns:
            Form | None: The parsed form
        """

    @abstractmethod
    def get_empty_form(self, req: ObjectWithHeaders) -> Form:
        """Get an empty parsed form object

        Args:
            req (ObjectWithHeaders): The originating request (used to get a boundary for multipart forms)

        Returns:
            Form: The empty form
        """

    @abstractmethod
    def deserialized_type(self) -> type[Form]:
        """Gets the form concrete type

        Returns:
            type[Form]: The form concrete type
        """

    @abstractmethod
    def import_form(self, exported: ExportedForm, req: ObjectWithHeaders) -> Form:
        """Imports a form exported by a serializer
            Used to convert a form from a Content-Type to another
            Information may be lost in the process

        Args:
            exported (ExportedForm): The exported form
            req: (ObjectWithHeaders): Used to get multipart boundary

        Returns:
            Form: The form converted to this serializer's format
        """

    @abstractmethod
    def export_form(self, source: Form) -> TupleExportedForm:
        """Formats a form so it can be imported by another serializer
            Information may be lost in the process

        Args:
            form (Form): The form to export

        Returns:
            ExportedForm: The exported form
        """
