from __future__ import annotations


from collections.abc import Mapping

import re
import string
import json
from typing import Any

import qs

from pyscalpel.http.body.abstract import (
    FormSerializer,
    TupleExportedForm,
    ExportedForm,
)
from pyscalpel.encoding import always_bytes
from pyscalpel.http.body.urlencoded import URLEncodedFormSerializer
from pyscalpel.utils import removesuffix

JSON_KEY_TYPES = str | int | float
JSON_VALUE_TYPES = (
    str
    | int
    | float
    | bool
    | None
    | list["JSON_VALUE_TYPES"]
    | dict[JSON_KEY_TYPES, "JSON_VALUE_TYPES"]
)


# TODO: JSON keys are actually only strings, so we should wrap
#   getter and setter  to always convert the keys to string.
class JSONForm(dict[JSON_KEY_TYPES, JSON_VALUE_TYPES]):
    """Form representing a JSON object {}

    Implemented by a plain dict

    Args:
        dict (_type_): A dict containing JSON-compatible types.
    """

    pass


def json_escape_bytes(data: bytes) -> str:
    printable = string.printable.encode("utf-8")

    return "".join(chr(ch) if ch in printable else f"\\u{ch:04x}" for ch in data)


def json_unescape(escaped: str) -> str:
    def decode_match(match):
        return chr(int(match.group(1), 16))

    return re.sub(r"\\u([0-9a-fA-F]{4})", decode_match, escaped)


def json_unescape_bytes(escaped: str) -> bytes:
    return json_unescape(escaped).encode("latin-1")


class PrintableJsonEncoder(json.JSONEncoder):
    def default(self, o: Any):
        if isinstance(o, bytes):
            return json_escape_bytes(o)
        return super().default(o)


def json_convert(value) -> JSON_VALUE_TYPES:
    return json.loads(json.dumps(value, cls=PrintableJsonEncoder))


def transform_tuple_to_dict(tup):
    """Transforms duplicates keys to list

    E.g:
    (("key_duplicate", 1),("key_duplicate", 2),("key_duplicate", 3),
    ("key_duplicate", 4),("key_uniq": "val") ,
    ("key_duplicate", 5),("key_duplicate", 6))
    ->
    {"key_duplicate": [1,2,3,4,5], "key_uniq": "val"}


    Args:
        tup (_type_): _description_

    Returns:
        _type_: _description_
    """
    result_dict = {}
    for pair in tup:
        key, value = pair
        converted_key: bytes | str
        match key:
            case bytes():
                converted_key = removesuffix(key, b"[]")
            case str():
                converted_key = removesuffix(key, "[]")
            case _:
                converted_key = key

        if converted_key in result_dict:
            if isinstance(result_dict[converted_key], list):
                result_dict[converted_key].append(value)
            else:
                result_dict[converted_key] = [result_dict[converted_key], value]
        else:
            result_dict[converted_key] = value
    return result_dict


def json_encode_exported_form(
    exported: TupleExportedForm,
) -> tuple[tuple[str, str], ...]:
    """Unicode escape (\\uXXXX) non printable bytes

    Args:
        exported (TupleExportedForm): The exported form tuple

    Returns:
        tuple[tuple[str, str], ...]: exported with every values as escaped strings
    """
    return tuple(
        (
            json_escape_bytes(key),
            json_escape_bytes(val or b""),
        )
        for key, val in exported
    )


def encode_JSON_form(
    d: dict[JSON_KEY_TYPES, JSON_VALUE_TYPES]
) -> dict[JSON_KEY_TYPES, JSON_VALUE_TYPES]:
    new_dict = {}
    for k, v in d.items():
        new_key = json_unescape(k) if isinstance(k, str) else k
        if isinstance(v, dict):
            new_value = encode_JSON_form(v)
        elif isinstance(v, str):
            new_value = json_unescape(v)
        else:
            new_value = v
        new_dict[new_key] = new_value
    return new_dict


class JSONFormSerializer(FormSerializer):
    def serialize(
        self, deserialized_body: Mapping[JSON_KEY_TYPES, JSON_VALUE_TYPES], req=...
    ) -> bytes:
        return json.dumps(deserialized_body).encode("utf-8")

    def deserialize(self, body: bytes, req=...) -> JSONForm | None:
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return None

        return JSONForm(parsed) if isinstance(parsed, dict) else None

    def get_empty_form(self, req=...) -> JSONForm:
        return JSONForm()

    def deserialized_type(self) -> type[JSONForm]:
        return JSONForm

    def export_form(self, source: JSONForm) -> TupleExportedForm:
        unescaped_source = encode_JSON_form(source)
        # Transform the dict to a php style query string
        serialized_to_qs = qs.build_qs(unescaped_source)

        # Parse the query string
        qs_parser = URLEncodedFormSerializer()
        parsed_qs = qs_parser.deserialize(always_bytes(serialized_to_qs))

        # Export the parsed query string to the tuple format
        tupled_form = qs_parser.export_form(parsed_qs)
        return tupled_form

    def import_form(self, exported: ExportedForm, req=...) -> JSONForm:
        # Parse array keys like "key1[key2][key3]" and place value to the correct path
        # e.g: ("key1[key2][key3]", "nested_value") -> {"key1": {"key2" : {"key3" : "nested_value"}}}
        dict_form = qs.qs_parse_pairs(list(json_encode_exported_form(exported)))
        json_form = JSONForm(dict_form.items())
        return json_form
