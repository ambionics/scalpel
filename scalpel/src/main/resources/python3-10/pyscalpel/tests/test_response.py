import unittest
from unittest.mock import MagicMock, patch
from pyscalpel.java.burp import IHttpHeader
from pyscalpel.http.response import *


class ResponseTestCase(unittest.TestCase):
    def test_from_mitmproxy(self):
        mitmproxy_response = MITMProxyResponse.make(
            200,
            b"Hello World!",
            Headers([(b"Content-Type", b"text/html")]),
        )
        response = Response.from_mitmproxy(mitmproxy_response)

        self.assertEqual("HTTP/1.1", response.http_version)
        self.assertEqual(200, response.status_code)
        self.assertEqual("OK", response.reason)

        # TODO: Add an update_content_length flag like in Request.
        #       (requires dropping mitmproxy and writting from scratch)
        del response.headers["Content-Length"]
        self.assertEqual(Headers([(b"Content-Type", b"text/html")]), response.headers)
        self.assertEqual(b"Hello World!", response.content)
        self.assertIsNone(response.trailers)

    def test_make(self):
        response = Response.make(
            status_code=200,
            content=b"Hello World!",
            headers=Headers([(b"Content-Type", b"text/html")]),
            host="localhost",
            port=8080,
            scheme="http",
        )

        # TODO: Add an update_content_length flag like in Request.
        #       (requires dropping mitmproxy and writting from scratch)
        del response.headers["Content-Length"]

        self.assertEqual("HTTP/1.1", response.http_version)
        self.assertEqual(200, response.status_code)
        self.assertEqual("OK", response.reason)
        self.assertEqual(Headers([(b"Content-Type", b"text/html")]), response.headers)
        self.assertEqual(b"Hello World!", response.content)
        self.assertIsNone(response.trailers)
        self.assertEqual("http", response.scheme)
        self.assertEqual("localhost", response.host)
        self.assertEqual(8080, response.port)

    def test_host_is(self):
        response = Response.make(200)
        response.host = "example.com"

        self.assertTrue(response.host_is("example.com"))
        self.assertFalse(response.host_is("google.com"))


class TestResponseMockedBasic(unittest.TestCase):
    def setUp(self):
        # Create a complete mock for IHttpResponse
        self.mock_response = MagicMock(spec=IHttpResponse)
        self.mock_response.httpVersion.return_value = "HTTP/1.1"
        self.mock_response.statusCode.return_value = 200
        self.mock_response.reasonPhrase.return_value = "OK"

        # Mocking headers to return a list of IHttpHeader mocks
        mock_header1 = MagicMock(spec=IHttpHeader)
        mock_header1.name.return_value = "Content-Type"
        mock_header1.value.return_value = "text/html"

        mock_header2 = MagicMock(spec=IHttpHeader)
        mock_header2.name.return_value = "Server"
        mock_header2.value.return_value = "Apache"

        self.mock_response.headers.return_value = [mock_header1, mock_header2]

        # Mocking body to return an IByteArray mock
        mock_body = MagicMock(spec=IByteArray)
        mock_body.getBytes.return_value = b"<html></html>"
        self.mock_response.body.return_value = mock_body

    @patch("pyscalpel.http.response.Headers.from_burp")
    def test_from_burp(self, mock_headers_from_burp):
        # Setup mock Headers.from_burp
        mock_headers_from_burp.return_value = Headers([])

        # Call the method under test
        response = Response.from_burp(self.mock_response)

        # Asserts
        self.assertEqual(response.http_version, "HTTP/1.1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.reason, "OK")
        self.assertEqual(response.content, b"<html></html>")
        mock_headers_from_burp.assert_called_once()


class TestResponseFromBurp(unittest.TestCase):
    def setUp(self):
        self.mock_response = MagicMock(spec=IHttpResponse)
        self.mock_response.httpVersion.return_value = "HTTP/1.1"
        self.mock_response.statusCode.return_value = 200
        self.mock_response.reasonPhrase.return_value = "OK"
        self.mock_response.headers.return_value = []
        self.mock_response.body.return_value = MagicMock(
            spec=IByteArray, getBytes=lambda: b"response body"
        )

        self.mock_service = MagicMock(spec=IHttpService)
        self.mock_service.secure.return_value = False
        self.mock_service.host.return_value = "example.com"
        self.mock_service.port.return_value = 80

        self.mock_request = MagicMock(spec=IHttpRequest)
        self.mock_request.httpService.return_value = self.mock_service

    @patch("pyscalpel.http.response.Headers.from_burp")
    @patch("pyscalpel.http.response.Request.from_burp")
    def test_from_burp_with_direct_request_and_service(
        self, mock_request_from_burp, mock_headers_from_burp
    ):
        mock_request_from_burp.return_value = MagicMock()
        mock_headers_from_burp.return_value = MagicMock()

        response = Response.from_burp(
            self.mock_response, self.mock_service, self.mock_request
        )

        mock_request_from_burp.assert_called_once_with(
            self.mock_request, self.mock_service
        )
        self.assertEqual(response.scheme, "http")
        self.assertEqual(response.host, "example.com")
        self.assertEqual(response.port, 80)

    @patch("pyscalpel.http.response.Headers.from_burp")
    @patch("pyscalpel.http.response.Request.from_burp")
    def test_from_burp_with_request_obtained_from_response(
        self, mock_request_from_burp, mock_headers_from_burp
    ):
        self.mock_response.initiatingRequest = MagicMock(return_value=self.mock_request)
        mock_request_from_burp.return_value = MagicMock()
        mock_headers_from_burp.return_value = MagicMock()

        response = Response.from_burp(self.mock_response)

        mock_request_from_burp.assert_called_once_with(self.mock_request, None)
        self.mock_request.httpService.assert_called_once()

    @patch("pyscalpel.http.response.Headers.from_burp")
    @patch("pyscalpel.http.response.Request.from_burp")
    def test_from_burp_with_secure_service(
        self, mock_request_from_burp, mock_headers_from_burp
    ):
        self.mock_service.secure.return_value = True
        mock_request_from_burp.return_value = MagicMock()
        mock_headers_from_burp.return_value = MagicMock()

        response = Response.from_burp(self.mock_response, self.mock_service)

        self.assertEqual(response.scheme, "https")


class TestResponseBytesConversion(unittest.TestCase):
    def test_response_to_bytes(self):
        # Example 1: Basic response with Content-Length header
        content1 = b"Hello World!"
        response1 = Response.make(
            status_code=200,
            content=content1,
            headers=((b"Content-Type", b"text/html"),),
            host="www.example.com",
            port=80,
            scheme="http",
        )
        # NOTE: The Content-Length header is automatically added by the MITMProxy Response object
        # MITMProxy sets headers to lowercase by default, so the Content-Length header is lowercase
        # If an existing Content-Length header with mixed case is already present, it will be not be overwritten
        # This is only the case for the Response object and not the Request, so it should probably not matter anyway.
        expected_bytes1 = (
            b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\ncontent-length: "
            + str(len(content1)).encode()
            + b"\r\n\r\nHello World!"
        )
        self.assertEqual(bytes(response1), expected_bytes1)

        # Example 2: More complex response with multiple headers, different scheme, and Content-Length header
        content2 = b"Not Found"
        response2 = Response.make(
            status_code=404,
            content=content2,
            headers=((b"Content-Type", b"text/plain"), (b"Server", b"TestServer")),
            host="www.another-example.com",
            port=443,
            scheme="https",
        )
        expected_bytes2 = (
            b"HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nServer: TestServer\r\ncontent-length: "
            + str(len(content2)).encode()
            + b"\r\n\r\nNot Found"
        )
        self.assertEqual(bytes(response2), expected_bytes2)


class TestResponseBodyProperty(unittest.TestCase):
    def test_body_property_and_bytes_output(self):
        # Initial response setup without unused parameters
        response = Response.make(
            status_code=200,
            content=b"Original content",
            headers=((b"Content-Type", b"text/plain"),),
        )

        # Update the body content
        new_content = b"Updated content"
        response.body = new_content

        # Check if the body property reflects the update
        self.assertEqual(response.body, new_content)

        # Build expected bytes output considering the update
        expected_bytes = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"content-length: " + str(len(new_content)).encode() + b"\r\n"
            b"\r\n"
            b"Updated content"
        )

        # Assuming the __bytes__ method correctly calculates and includes the Content-Length header
        # and other details based on the current state of the Response object
        self.assertEqual(bytes(response), expected_bytes)


if __name__ == "__main__":
    unittest.main()
