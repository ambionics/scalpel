"""Pythonic wrappers for the Burp Request Java object """

from __future__ import annotations

import urllib.parse
import re

from typing import (
    Iterable,
    Literal,
    cast,
    Sequence,
    Any,
    MutableMapping,
    Mapping,
    TYPE_CHECKING,
)
from copy import deepcopy
from pyscalpel.java.burp import (
    IHttpRequest,
    HttpRequest,
    IHttpService,
    HttpService,
    IByteArray,
)
from pyscalpel.burp_utils import get_bytes
from pyscalpel.java.scalpel_types.utils import PythonUtils
from pyscalpel.encoding import always_bytes, always_str
from pyscalpel.http.headers import Headers
from pyscalpel.http.mime import get_header_value_without_params
from pyscalpel.http.utils import host_is, match_patterns
from pyscalpel.http.body import (
    FormSerializer,
    JSONFormSerializer,
    URLEncodedFormSerializer,
    MultiPartFormSerializer,
    MultiPartForm,
    URLEncodedFormView,
    URLEncodedForm,
    JSON_KEY_TYPES,
    JSON_VALUE_TYPES,
    CONTENT_TYPE_TO_SERIALIZER,
    JSONForm,
    IMPLEMENTED_CONTENT_TYPES,
    ImplementedContentType,
)

from _internal_mitmproxy.coretypes import multidict
from _internal_mitmproxy.net.http.url import (
    parse as url_parse,
    unparse as url_unparse,
    encode as url_encode,
    decode as url_decode,
)
from _internal_mitmproxy.net.http import cookies

if TYPE_CHECKING:  # pragma: no cover
    from pyscalpel.http.response import Response


class FormNotParsedException(Exception):
    """Exception raised when a form deserialization failed

    Args:
        Exception (Exception): The base exception
    """


class Request:
    """A "Burp oriented" HTTP request class


    This class allows to manipulate Burp requests in a Pythonic way.
    """

    _Port = int
    _QueryParam = tuple[str, str]
    _ParsedQuery = tuple[_QueryParam, ...]
    _HttpVersion = str
    _HeaderKey = str
    _HeaderValue = str
    _Header = tuple[_HeaderKey, _HeaderValue]
    _Host = str
    _Method = str
    _Scheme = Literal["http", "https"]
    _Authority = str
    _Content = bytes
    _Path = str

    host: _Host
    port: _Port
    method: _Method
    scheme: _Scheme
    authority: _Authority

    # Path also includes URI parameters (;), query (?) and fragment (#)
    # Simply because it is more conveninent to manipulate that way in a pentensting context
    # It also mimics the way mitmproxy works.
    path: _Path

    http_version: _HttpVersion
    _headers: Headers
    _serializer: FormSerializer | None = None
    _deserialized_content: Any = None
    _content: _Content | None = None
    _old_deserialized_content: Any = None
    _is_form_initialized: bool = False
    update_content_length: bool = True

    def __init__(
        self,
        method: str,
        scheme: Literal["http", "https"],
        host: str,
        port: int,
        path: str,
        http_version: str,
        headers: (
            Headers | tuple[tuple[bytes, bytes], ...] | Iterable[tuple[bytes, bytes]]
        ),
        authority: str,
        content: bytes | None,
    ):
        self.scheme = scheme
        self.host = host
        self.port = port
        self.path = path
        self.method = method
        self.authority = authority
        self.http_version = http_version
        self.headers = headers if isinstance(headers, Headers) else Headers(headers)
        self._content = content

        # Initialize the serializer (json,urlencoded,multipart)
        self.update_serializer_from_content_type(
            self.headers.get("Content-Type"), fail_silently=True
        )

        # Initialize old deserialized content to avoid modifying content if it has not been modified
        # (see test_content_do_not_modify_json() in scalpel/src/main/resources/python/pyscalpel/tests/test_request.py)
        self._old_deserialized_content = deepcopy(self._deserialized_content)

    def _del_header(self, header: str) -> bool:
        if header in self._headers.keys():
            del self._headers[header]
            return True

        return False

    def _update_content_length(self) -> None:
        if self.update_content_length:
            if self._content is None:
                self._del_header("Content-Length")
            else:
                length = len(cast(bytes, self._content))
                self._headers["Content-Length"] = str(length)

    @staticmethod
    def _parse_qs(query_string: str) -> _ParsedQuery:
        return tuple(urllib.parse.parse_qsl(query_string))

    @staticmethod
    def _parse_url(
        url: str,
    ) -> tuple[_Scheme, _Host, _Port, _Path]:
        scheme, host, port, path = url_parse(url)

        # This method is only used to create HTTP requests from URLs
        #   so we can ensure the scheme is valid for this usage
        if scheme not in (b"http", b"https"):
            scheme = b"http"

        return cast(
            tuple[Literal["http", "https"], str, int, str],
            (scheme.decode("ascii"), host.decode("idna"), port, path.decode("ascii")),
        )

    @staticmethod
    def _unparse_url(scheme: _Scheme, host: _Host, port: _Port, path: _Path) -> str:
        return url_unparse(scheme, host, port, path)

    @classmethod
    def make(
        cls,
        method: str,
        url: str,
        content: bytes | str = "",
        headers: (
            Headers
            | dict[str | bytes, str | bytes]
            | dict[str, str]
            | dict[bytes, bytes]
            | Iterable[tuple[bytes, bytes]]
        ) = (),
    ) -> Request:
        """Create a request from an URL

        Args:
            method (str): The request method (GET,POST,PUT,PATCH, DELETE,TRACE,...)
            url (str): The request URL
            content (bytes | str, optional): The request content. Defaults to "".
            headers (Headers, optional): The request headers. Defaults to ().

        Returns:
            Request: The HTTP request
        """
        scalpel_headers: Headers
        match headers:
            case Headers():
                scalpel_headers = headers
            case dict():
                casted_headers = cast(dict[str | bytes, str | bytes], headers)
                scalpel_headers = Headers(
                    (
                        (always_bytes(key), always_bytes(val))
                        for key, val in casted_headers.items()
                    )
                )
            case _:
                scalpel_headers = Headers(headers)

        scheme, host, port, path = Request._parse_url(url)
        http_version = "HTTP/1.1"

        # Inferr missing Host header from URL
        host_header = scalpel_headers.get("Host")
        if host_header is None:
            match (scheme, port):
                case ("http", 80) | ("https", 443):
                    host_header = host
                case _:
                    host_header = f"{host}:{port}"

            scalpel_headers["Host"] = host_header

        authority: str = host_header
        encoded_content = always_bytes(content)

        assert isinstance(host, str)

        return cls(
            method=method,
            scheme=scheme,
            host=host,
            port=port,
            path=path,
            http_version=http_version,
            headers=scalpel_headers,
            authority=authority,
            content=encoded_content,
        )

    @classmethod
    def from_burp(
        cls, request: IHttpRequest, service: IHttpService | None = None
    ) -> Request:  # pragma: no cover (uses Java API)
        """Construct an instance of the Request class from a Burp suite HttpRequest.
        :param request: The Burp suite HttpRequest to convert.
        :return: A Request with the same data as the Burp suite HttpRequest.
        """
        service = service or request.httpService()
        body = get_bytes(request.body())

        # Burp will give you lowercased and pseudo headers when using HTTP/2.
        # https://portswigger.net/burp/documentation/desktop/http2/http2-normalization-in-the-message-editor#sending-requests-without-any-normalization:~:text=are%20converted%20to-,lowercase,-.
        # https://blog.yaakov.online/http-2-header-casing/
        headers: Headers = Headers.from_burp(request.headers())

        # Burp gives a 0 length byte array body even when it doesn't exist, instead of null.
        # Empty but existing bodies without a Content-Length header are lost in the process.
        if not body and not headers.get("Content-Length"):
            body = None

        # request.url() gives a relative url for some reason
        # So we have to parse and unparse to get the full path
        #   (path + parameters + query + fragment)
        _, _, path, parameters, query, fragment = urllib.parse.urlparse(request.url())

        # Concatenate the path components
        # Empty parameters,query and fragment are lost in the process
        # e.g.: http://example.com;?# becomes http://example.com
        # To use such an URL, the user must set the path directly
        # To fix this we would need to write our own URL parser, which is a bit overkill for now.
        path = urllib.parse.urlunparse(("", "", path, parameters, query, fragment))

        host = ""
        port = 0
        scheme = "http"
        if service:
            host = service.host()
            port = service.port()
            scheme = "https" if service.secure() else "http"

        return cls(
            method=request.method(),
            scheme=scheme,
            host=host,
            port=port,
            path=path,
            http_version=request.httpVersion() or "HTTP/1.1",
            headers=headers,
            authority=headers.get(":authority") or headers.get("Host") or "",
            content=body,
        )

    def __bytes__(self) -> bytes:
        """Convert the request to bytes
        :return: The request as bytes.
        """
        # Reserialize the request to bytes.
        first_line = (
            b" ".join(
                always_bytes(s) for s in (self.method, self.path, self.http_version)
            )
            + b"\r\n"
        )

        # Strip HTTP/2 pseudo headers.
        # https://portswigger.net/burp/documentation/desktop/http2/http2-basics-for-burp-users#:~:text=HTTP/2%20specification.-,Pseudo%2Dheaders,-In%20HTTP/2
        mapped_headers = tuple(
            field for field in self.headers.fields if not field[0].startswith(b":")
        )

        if self.headers.get(b"Host") is None and self.http_version == "HTTP/2":
            # Host header is not present in HTTP/2, but is required by Burp message editor.
            # So we have to add it back from the :authority pseudo-header.
            # https://portswigger.net/burp/documentation/desktop/http2/http2-normalization-in-the-message-editor#sending-requests-without-any-normalization:~:text=pseudo%2Dheaders%20and-,derives,-the%20%3Aauthority%20from
            mapped_headers = (
                (b"Host", always_bytes(self.headers[":authority"])),
            ) + tuple(mapped_headers)

        # Construct the request's headers part.
        headers_lines = b"".join(
            b"%s: %s\r\n" % (key, val) for key, val in mapped_headers
        )

        # Set a default value for the request's body. (None -> b"")
        body = self.content or b""

        # Construct the whole request and return it.
        return first_line + headers_lines + b"\r\n" + body

    def to_burp(self) -> IHttpRequest:  # pragma: no cover
        """Convert the request to a Burp suite :class:`IHttpRequest`.
        :return: The request as a Burp suite :class:`IHttpRequest`.
        """
        # Convert the request to a Burp ByteArray.
        request_byte_array: IByteArray = PythonUtils.toByteArray(bytes(self))

        if self.port == 0:
            # No networking information is available, so we build a plain network-less request.
            return HttpRequest.httpRequest(request_byte_array)

        # Build the Burp HTTP networking service.
        service: IHttpService = HttpService.httpService(
            self.host, self.port, self.scheme == "https"
        )

        # Instantiate and return a new Burp HTTP request.
        return HttpRequest.httpRequest(service, request_byte_array)

    @classmethod
    def from_raw(
        cls,
        data: bytes | str,
        real_host: str = "",
        port: int = 0,
        scheme: Literal["http"] | Literal["https"] | str = "http",
    ) -> Request:  # pragma: no cover
        """Construct an instance of the Request class from raw bytes.
        :param data: The raw bytes to convert.
        :param real_host: The real host to connect to.
        :param port: The port of the request.
        :param scheme: The scheme of the request.
        :return: A :class:`Request` with the same data as the raw bytes.
        """
        # Convert the raw bytes to a Burp ByteArray.
        # We use the Burp API to trivialize the parsing of the request from raw bytes.
        str_or_byte_array: IByteArray | str = (
            data if isinstance(data, str) else PythonUtils.toByteArray(data)
        )

        # Handle the case where the networking informations are not provided.
        if port == 0:
            # Instantiate and return a new Burp HTTP request without networking informations.
            burp_request: IHttpRequest = HttpRequest.httpRequest(str_or_byte_array)
        else:
            # Build the Burp HTTP networking service.
            service: IHttpService = HttpService.httpService(
                real_host, port, scheme == "https"
            )

            # Instantiate a new Burp HTTP request with networking informations.
            burp_request: IHttpRequest = HttpRequest.httpRequest(
                service, str_or_byte_array
            )

        # Construct the request from the Burp.
        return cls.from_burp(burp_request)

    @property
    def url(self) -> str:
        """
        The full URL string, constructed from `Request.scheme`,
            `Request.host`, `Request.port` and `Request.path`.

        Setting this property updates these attributes as well.
        """
        return Request._unparse_url(self.scheme, self.host, self.port, self.path)

    @url.setter
    def url(self, val: str | bytes) -> None:
        (self.scheme, self.host, self.port, self.path) = Request._parse_url(
            always_str(val)
        )

    def _get_query(self) -> _ParsedQuery:
        query = urllib.parse.urlparse(self.url).query
        return tuple(url_decode(query))

    def _set_query(self, query_data: Sequence[_QueryParam]):
        query = url_encode(query_data)
        _, _, path, params, _, fragment = urllib.parse.urlparse(self.url)
        self.path = urllib.parse.urlunparse(["", "", path, params, query, fragment])

    @property
    def query(self) -> URLEncodedFormView:
        """The query string parameters as a dict-like object

        Returns:
            QueryParamsView: The query string parameters
        """
        return URLEncodedFormView(
            multidict.MultiDictView(self._get_query, self._set_query)
        )

    @query.setter
    def query(self, value: Sequence[tuple[str, str]]):
        self._set_query(value)

    def _has_deserialized_content_changed(self) -> bool:
        return self._deserialized_content != self._old_deserialized_content

    def _serialize_content(self):
        if self._serializer is None:
            return

        if self._deserialized_content is None:
            self._content = None
            return

        self._update_serialized_content(
            self._serializer.serialize(self._deserialized_content, req=self)
        )

    def _update_serialized_content(self, serialized: bytes):
        if self._serializer is None:
            self._content = serialized
            return

        # Update the parsed form
        self._deserialized_content = self._serializer.deserialize(serialized, self)
        self._old_deserialized_content = deepcopy(self._deserialized_content)

        # Set the raw content directly
        self._content = serialized

    def _deserialize_content(self):
        if self._serializer is None:
            return

        if self._content:
            self._deserialized_content = self._serializer.deserialize(
                self._content, req=self
            )

    def _update_deserialized_content(self, deserialized: Any):
        if self._serializer is None:
            return

        if deserialized is None:
            self._deserialized_content = None
            self._old_deserialized_content = None
            return

        self._deserialized_content = deserialized
        self._content = self._serializer.serialize(deserialized, self)
        self._update_content_length()

    @property
    def content(self) -> bytes | None:
        """The request content / body as raw bytes

        Returns:
            bytes | None: The content if it exists
        """
        if self._serializer and self._has_deserialized_content_changed():
            self._update_deserialized_content(self._deserialized_content)
            self._old_deserialized_content = deepcopy(self._deserialized_content)

        self._update_content_length()

        return self._content

    @content.setter
    def content(self, value: bytes | str | None):
        match value:
            case None:
                self._content = None
                self._deserialized_content = None
                return
            case str():
                value = value.encode("latin-1")

        self._update_content_length()

        self._update_serialized_content(value)

    @property
    def body(self) -> bytes | None:
        """Alias for content()

        Returns:
            bytes | None: The request body / content
        """
        return self.content

    @body.setter
    def body(self, value: bytes | str | None):
        self.content = value

    def update_serializer_from_content_type(
        self,
        content_type: ImplementedContentType | str | None = None,
        fail_silently: bool = False,
    ):
        """Update the form parsing based on the given Content-Type

        Args:
            content_type (ImplementedContentTypesTp | str | None, optional): The form content-type. Defaults to None.
            fail_silently (bool, optional): Determine if an excpetion is raised when the content-type is unknown. Defaults to False.

        Raises:
            FormNotParsedException: Raised when the content-type is unknown.
        """
        # Strip the boundary param so we can use our content-type to serializer map
        _content_type: str = get_header_value_without_params(
            content_type or self.headers.get("Content-Type") or ""
        )

        serializer = None
        if _content_type in IMPLEMENTED_CONTENT_TYPES:
            serializer = CONTENT_TYPE_TO_SERIALIZER.get(_content_type)

        if serializer is None:
            if fail_silently:
                serializer = self._serializer
            else:
                raise FormNotParsedException(
                    f"Unimplemented form content-type: {_content_type}"
                )
        self._set_serializer(serializer)

    @property
    def content_type(self) -> str | None:
        """The Content-Type header value.

        Returns:
            str | None: <=> self.headers.get("Content-Type")
        """
        return self.headers.get("Content-Type")

    @content_type.setter
    def content_type(self, value: str) -> str | None:
        self.headers["Content-Type"] = value

    def create_defaultform(
        self,
        content_type: ImplementedContentType | str | None = None,
        update_header: bool = True,
    ) -> MutableMapping[Any, Any]:
        """Creates the form if it doesn't exist, else returns the existing one

        Args:
            content_type (IMPLEMENTED_CONTENT_TYPES_TP | None, optional): The form content-type. Defaults to None.
            update_header (bool, optional): Whether to update the header. Defaults to True.

        Raises:
            FormNotParsedException: Thrown when provided content-type has no implemented form-serializer
            FormNotParsedException: Thrown when the raw content could not be parsed.

        Returns:
            MutableMapping[Any, Any]: The mapped form.
        """
        if not self._is_form_initialized or content_type:
            self.update_serializer_from_content_type(content_type)

            # Set content-type if it does not exist
            if (content_type and update_header) or not self.headers.get_all(
                "Content-Type"
            ):
                self.headers["Content-Type"] = content_type

        serializer = self._serializer
        if serializer is None:
            # This should probably never trigger here as it should already be raised by update_serializer_from_content_type
            raise FormNotParsedException(
                f"Form of content-type {self.content_type} not implemented."
            )

        # Create default form.
        if not self.content:
            self._deserialized_content = serializer.get_empty_form(self)
        elif self._deserialized_content is None:
            self._deserialize_content()

        if self._deserialized_content is None:
            raise FormNotParsedException(
                f"Could not parse content to {serializer.deserialized_type()}\nContent:{self._content}"
            )

        if not isinstance(self._deserialized_content, serializer.deserialized_type()):
            self._deserialized_content = serializer.get_empty_form(self)

        self._is_form_initialized = True
        return self._deserialized_content

    @property
    def form(self) -> MutableMapping[Any, Any]:
        """Mapping from content parsed accordingly to Content-Type

        Raises:
            FormNotParsedException: The content could not be parsed accordingly to Content-Type

        Returns:
            MutableMapping[Any, Any]: The mapped request form
        """
        if not self._is_form_initialized:
            self.update_serializer_from_content_type()

        self.create_defaultform()
        if self._deserialized_content is None:
            raise FormNotParsedException()

        self._is_form_initialized = True
        return self._deserialized_content

    @form.setter
    def form(self, form: MutableMapping[Any, Any]):
        if not self._is_form_initialized:
            self.update_serializer_from_content_type()
            self._is_form_initialized = True

        self._deserialized_content = form

        # Update raw _content
        self._serialize_content()

    def _set_serializer(self, serializer: FormSerializer | None):
        # Update the serializer
        old_serializer = self._serializer
        self._serializer = serializer

        if serializer is None:
            self._deserialized_content = None
            return

        if type(serializer) == type(old_serializer):
            return

        if old_serializer is None:
            self._deserialize_content()
            return

        old_form = self._deserialized_content

        if old_form is None:
            self._deserialize_content()
            return

        # Convert the form to an intermediate format for easier conversion
        exported_form = old_serializer.export_form(old_form)

        # Parse the intermediate data to the new serializer format
        imported_form = serializer.import_form(exported_form, self)
        self._deserialized_content = imported_form

    def _update_serializer_and_get_form(
        self, serializer: FormSerializer
    ) -> MutableMapping[Any, Any] | None:
        # Set the serializer and update the content
        self._set_serializer(serializer)

        # Return the new form
        return self._deserialized_content

    def _update_serializer_and_set_form(
        self, serializer: FormSerializer, form: MutableMapping[Any, Any]
    ) -> None:
        # NOOP when the serializer is the same
        self._set_serializer(serializer)

        self._update_deserialized_content(form)

    @property
    def urlencoded_form(self) -> URLEncodedForm:
        """The urlencoded form data

        Converts the content to the urlencoded form format if needed.
        Modification to this object will update Request.content and vice versa

        Returns:
            QueryParams: The urlencoded form data
        """
        self._is_form_initialized = True
        return cast(
            URLEncodedForm,
            self._update_serializer_and_get_form(URLEncodedFormSerializer()),
        )

    @urlencoded_form.setter
    def urlencoded_form(self, form: URLEncodedForm):
        self._is_form_initialized = True
        self._update_serializer_and_set_form(URLEncodedFormSerializer(), form)

    @property
    def json_form(self) -> dict[JSON_KEY_TYPES, JSON_VALUE_TYPES]:
        """The JSON form data

        Converts the content to the JSON form format if needed.
        Modification to this object will update Request.content and vice versa

        Returns:
          dict[JSON_KEY_TYPES, JSON_VALUE_TYPES]: The JSON form data
        """
        self._is_form_initialized = True
        if self._update_serializer_and_get_form(JSONFormSerializer()) is None:
            serializer = cast(JSONFormSerializer, self._serializer)
            self._deserialized_content = serializer.get_empty_form(self)

        return self._deserialized_content

    @json_form.setter
    def json_form(self, form: dict[JSON_KEY_TYPES, JSON_VALUE_TYPES]):
        self._is_form_initialized = True
        self._update_serializer_and_set_form(JSONFormSerializer(), JSONForm(form))

    def _ensure_multipart_content_type(self) -> str:
        content_types_headers = self.headers.get_all("Content-Type")
        pattern = re.compile(
            r"^multipart/form-data;\s*boundary=([^;\s]+)", re.IGNORECASE
        )

        # Find a valid multipart content-type header with a valid boundary
        matched_content_type: str | None = None
        for content_type in content_types_headers:
            if pattern.match(content_type):
                matched_content_type = content_type
                break

        # If no boundary was found, overwrite the Content-Type header
        # If an user wants to avoid this behaviour,they should manually create a MultiPartForm(), convert it to bytes
        #   and pass it as raw_form()
        if matched_content_type is None:
            # TODO: Randomly generate this? The boundary could be used to fingerprint Scalpel
            new_content_type = (
                "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
            )
            self.headers["Content-Type"] = new_content_type
            return new_content_type

        return matched_content_type

    @property
    def multipart_form(self) -> MultiPartForm:
        """The multipart form data

        Converts the content to the multipart form format if needed.
        Modification to this object will update Request.content and vice versa

        Returns:
            MultiPartForm
        """
        self._is_form_initialized = True

        # Keep boundary even if content-type has changed
        if isinstance(self._deserialized_content, MultiPartForm):
            return self._deserialized_content

        # We do not have an existing form, so we have to ensure we have a content-type header with a boundary
        self._ensure_multipart_content_type()

        # Serialize the current form and try to parse it with the new serializer
        form = self._update_serializer_and_get_form(MultiPartFormSerializer())
        serializer = cast(MultiPartFormSerializer, self._serializer)

        # Set a default value
        if not form:
            self._deserialized_content = serializer.get_empty_form(self)

        # get_empty_form() fails when the request doesn't have a valid Content-Type multipart/form-data with a boundary
        if self._deserialized_content is None:
            raise FormNotParsedException(
                f"Could not parse content to {serializer.deserialized_type()}"
            )

        return self._deserialized_content

    @multipart_form.setter
    def multipart_form(self, form: MultiPartForm):
        self._is_form_initialized = True
        if not isinstance(self._deserialized_content, MultiPartForm):
            # Generate a multipart header because we don't have any boundary to format the multipart.
            self._ensure_multipart_content_type()

        return self._update_serializer_and_set_form(
            MultiPartFormSerializer(), cast(MutableMapping, form)
        )

    @property
    def cookies(self) -> multidict.MultiDictView[str, str]:
        """
        The request cookies.
        For the most part, this behaves like a dictionary.
        Modifications to the MultiDictView update `Request.headers`, and vice versa.
        """
        return multidict.MultiDictView(self._get_cookies, self._set_cookies)

    def _get_cookies(self) -> tuple[tuple[str, str], ...]:
        header = self.headers.get_all("Cookie")
        return tuple(cookies.parse_cookie_headers(header))

    def _set_cookies(self, value: tuple[tuple[str, str], ...]):
        self.headers["cookie"] = cookies.format_cookie_header(value)

    @cookies.setter
    def cookies(self, value: tuple[tuple[str, str], ...] | Mapping[str, str]):
        if hasattr(value, "items") and callable(getattr(value, "items")):
            value = tuple(cast(Mapping[str, str], value).items())
        self._set_cookies(cast(tuple[tuple[str, str], ...], value))

    @property
    def host_header(self) -> str | None:
        """Host header value

        Returns:
            str | None: The host header value
        """
        return self.headers.get("Host")

    @host_header.setter
    def host_header(self, value: str | None):
        self.headers["Host"] = value

    def text(self, encoding="utf-8") -> str:
        """The decoded content

        Args:
            encoding (str, optional): encoding to use. Defaults to "utf-8".

        Returns:
            str: The decoded content
        """
        if self.content is None:
            return ""

        return self.content.decode(encoding)

    @property
    def headers(self) -> Headers:
        """The request HTTP headers

        Returns:
            Headers: a case insensitive dict containing the HTTP headers
        """
        self._update_content_length()
        return self._headers

    @headers.setter
    def headers(self, value: Headers):
        self._headers = value
        self._update_content_length()

    @property
    def content_length(self) -> int:
        """Returns the Content-Length header value
           Returns 0 if the header is absent

        Args:
            value (int | str): The Content-Length value

        Raises:
            RuntimeError: Throws RuntimeError when the value is invalid
        """
        content_length: str | None = self.headers.get("Content-Length")
        if content_length is None:
            return 0

        trimmed = content_length.strip()
        if not trimmed.isdigit():
            raise ValueError("Content-Length does not contain only digits")

        return int(trimmed)

    @content_length.setter
    def content_length(self, value: int | str):
        if self.update_content_length:
            # It is useless to manually set content-length because the value will be erased.
            raise RuntimeError(
                "Cannot set content_length when self.update_content_length is True"
            )

        if isinstance(value, int):
            value = str(value)

        self._headers["Content-Length"] = value

    @property
    def pretty_host(self) -> str:
        """Returns the most approriate host
        Returns self.host when it exists, else it returns self.host_header

        Returns:
            str: The request target host
        """
        return self.host or self.headers.get("Host") or ""

    def host_is(self, *patterns: str) -> bool:
        """Perform wildcard matching (fnmatch) on the target host.

        Args:
            pattern (str): The pattern to use

        Returns:
            bool: Whether the pattern matches
        """
        return host_is(self.pretty_host, *patterns)

    def path_is(self, *patterns: str) -> bool:
        return match_patterns(self.path, *patterns)
