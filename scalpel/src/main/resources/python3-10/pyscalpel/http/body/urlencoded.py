from __future__ import annotations
from urllib.parse import quote_from_bytes as quote, parse_qsl
from typing import Any, Iterable

import sys
import qs
from pyscalpel.encoding import always_bytes, always_str
from pyscalpel.http.body.abstract import (
    ExportedForm,
    TupleExportedForm,
)

from _internal_mitmproxy.coretypes import multidict

from .abstract import FormSerializer, ExportedForm


class URLEncodedFormView(multidict.MultiDictView[str, str]):
    def __init__(self, origin: multidict.MultiDictView[str, str]) -> None:
        super().__init__(origin._getter, origin._setter)

    def __setitem__(self, key: int | str | bytes, value: int | str | bytes) -> None:
        super().__setitem__(always_str(key), always_str(value))


class URLEncodedForm(multidict.MultiDict[bytes, bytes]):
    def __init__(self, fields: Iterable[tuple[str | bytes, str | bytes]]) -> None:
        fields_converted_to_bytes: Iterable[tuple[bytes, bytes]] = (
            (
                always_bytes(key),
                always_bytes(val),
            )
            for (key, val) in fields
        )
        super().__init__(fields_converted_to_bytes)

    def __setitem__(self, key: int | str | bytes, value: int | str | bytes) -> None:
        super().__setitem__(always_bytes(key), always_bytes(value))

    def __getitem__(self, key: int | bytes | str) -> bytes:
        return super().__getitem__(always_bytes(key))


def convert_for_urlencode(val: str | float | bool | bytes | int) -> str | bytes:
    match val:
        case bytes():
            return val
        case bool():
            return "1" if val else "0"
        case _:
            return str(val)


class URLEncodedFormSerializer(FormSerializer):
    def serialize(
        self, deserialized_body: multidict.MultiDict[bytes, bytes], req=...
    ) -> bytes:
        return b"&".join(
            b"=".join(quote(kv, safe="[]").encode() for kv in field)
            for field in deserialized_body.fields
        )

    def deserialize(self, body: bytes, req=...) -> URLEncodedForm:
        try:
            # XXX: urllib is broken when passing bytes to parse_qsl because it tries to decode it
            # but doesn't pass the specified encoding and instead the internal one is used (i.e: ascii, which can't decode some bytes)
            # This should be enough:
            # fields = urllib.parse.parse_qsl(body)

            # But because urllib is broken we need all of this:
            # (I may be wrong)
            decoded = body.decode("latin-1")
            parsed = parse_qsl(decoded, keep_blank_values=True)
            fields = (
                (
                    key.encode("latin-1"),
                    val.encode("latin-1"),
                )
                for key, val in parsed
            )
            return URLEncodedForm(fields)
        except UnicodeEncodeError as exc:  # pragma: no cover
            print("Query string crashed urrlib parser:", body, file=sys.stderr)
            raise exc

    def get_empty_form(self, req=...) -> Any:
        return URLEncodedForm(tuple())

    def deserialized_type(self) -> type[URLEncodedForm]:
        return URLEncodedForm

    def import_form(self, exported: ExportedForm, req=...) -> URLEncodedForm:
        match exported:
            case tuple():
                fields = list()
                for key, val in exported:
                    # Skip null values
                    if val is None:
                        continue

                    # Convert key,val as str
                    fields.append(
                        (convert_for_urlencode(key), convert_for_urlencode(val))
                    )
                return URLEncodedForm(fields)
            case dict():
                mapped_qs = qs.build_qs(exported)
                return self.deserialize(mapped_qs.encode())

    def export_form(self, source: URLEncodedForm) -> TupleExportedForm:
        return source.fields
