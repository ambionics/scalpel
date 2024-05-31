from __future__ import annotations


from typing import Literal, get_args

from pyscalpel.http.body.abstract import *
from pyscalpel.http.body.json_form import *
from pyscalpel.http.body.multipart import *
from pyscalpel.http.body.urlencoded import *


# In Python 3.11 it should be possible to do
#   IMPLEMENTED_CONTENT_TYPES_TP = Type[*IMPLEMENTED_CONTENT_TYPES]
ImplementedContentType = Literal[
    "application/x-www-form-urlencoded", "application/json", "multipart/form-data"
]

IMPLEMENTED_CONTENT_TYPES: set[ImplementedContentType] = set(
    get_args(ImplementedContentType)
)


CONTENT_TYPE_TO_SERIALIZER: dict[ImplementedContentType, FormSerializer] = {
    "application/x-www-form-urlencoded": URLEncodedFormSerializer(),
    "application/json": JSONFormSerializer(),
    "multipart/form-data": MultiPartFormSerializer(),
}
