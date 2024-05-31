import contextlib
import datetime
import ipaddress
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Optional, Union, Dict, List, NewType

# from cryptography import x509
# from cryptography.hazmat.primitives import hashes, serialization
# from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec
# from cryptography.hazmat.primitives.serialization import pkcs12
# from cryptography.x509 import NameOID, ExtendedKeyUsageOID

# import OpenSSL

from _internal_mitmproxy.coretypes import serializable

# Default expiry must not be too long: https://github.com/_internal_mitmproxy/_internal_mitmproxy/issues/815
CA_EXPIRY = datetime.timedelta(days=10 * 365)
CERT_EXPIRY = datetime.timedelta(days=365)

# Generated with "openssl dhparam". It's too slow to generate this on startup.
DEFAULT_DHPARAM = b"""
-----BEGIN DH PARAMETERS-----
MIICCAKCAgEAyT6LzpwVFS3gryIo29J5icvgxCnCebcdSe/NHMkD8dKJf8suFCg3
O2+dguLakSVif/t6dhImxInJk230HmfC8q93hdcg/j8rLGJYDKu3ik6H//BAHKIv
j5O9yjU3rXCfmVJQic2Nne39sg3CreAepEts2TvYHhVv3TEAzEqCtOuTjgDv0ntJ
Gwpj+BJBRQGG9NvprX1YGJ7WOFBP/hWU7d6tgvE6Xa7T/u9QIKpYHMIkcN/l3ZFB
chZEqVlyrcngtSXCROTPcDOQ6Q8QzhaBJS+Z6rcsd7X+haiQqvoFcmaJ08Ks6LQC
ZIL2EtYJw8V8z7C0igVEBIADZBI6OTbuuhDwRw//zU1uq52Oc48CIZlGxTYG/Evq
o9EWAXUYVzWkDSTeBH1r4z/qLPE2cnhtMxbFxuvK53jGB0emy2y1Ei6IhKshJ5qX
IB/aE7SSHyQ3MDHHkCmQJCsOd4Mo26YX61NZ+n501XjqpCBQ2+DfZCBh8Va2wDyv
A2Ryg9SUz8j0AXViRNMJgJrr446yro/FuJZwnQcO3WQnXeqSBnURqKjmqkeFP+d8
6mk2tqJaY507lRNqtGlLnj7f5RNoBFJDCLBNurVgfvq9TCVWKDIFD4vZRjCrnl6I
rD693XKIHUCWOjMh1if6omGXKHH40QuME2gNa50+YPn1iYDl88uDbbMCAQI=
-----END DH PARAMETERS-----
"""


class Cert(serializable.Serializable): ...


def _name_to_keyval(name) -> List[Tuple[str, str]]:
    parts = []
    for attr in name:
        # pyca cryptography <35.0.0 backwards compatiblity
        if hasattr(name, "rfc4514_attribute_name"):  # pragma: no cover
            k = attr.rfc4514_attribute_name  # type: ignore
        else:  # pragma: no cover
            k = attr.rfc4514_string().partition("=")[0]
        v = attr.value
        parts.append((k, v))
    return parts


def create_ca(
    organization: str,
    cn: str,
    key_size: int,
): ...


def dummy_cert(
    privkey,
    cacert,
    commonname: Optional[str],
    sans: List[str],
    organization: Optional[str] = None,
) -> Cert: ...


@dataclass(frozen=True)
class CertStoreEntry: ...


TCustomCertId = str  # manually provided certs (e.g. _internal_mitmproxy's --certs)
TGeneratedCertId = Tuple[Optional[str], Tuple[str, ...]]  # (common_name, sans)
TCertId = Union[TCustomCertId, TGeneratedCertId]

DHParams = NewType("DHParams", bytes)


class CertStore: ...


def load_pem_private_key(
    data: bytes, password: Optional[bytes]
): ...
