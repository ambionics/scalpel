import unittest

from unittest.mock import MagicMock

from pyscalpel.http.flow import *


class FlowTestCase(unittest.TestCase):
    def test_construct_default(self):
        flow = Flow()

        self.assertEqual("http", flow.scheme)
        self.assertEqual("", flow.host)
        self.assertEqual(0, flow.port)
        self.assertEqual(None, flow.request)
        self.assertEqual(None, flow.response)
        self.assertEqual(None, flow.text)

    def test_construct(self):
        request = Request.make("GET", "https://localhost")
        response = Response.make(200)
        flow = Flow(
            scheme="https",
            host="localhost",
            port=443,
            request=request,
            response=response,
            text=b"Hello world!",
        )

        self.assertEqual("https", flow.scheme)
        self.assertEqual("localhost", flow.host)
        self.assertEqual(443, flow.port)
        self.assertEqual(request, flow.request)
        self.assertEqual(response, flow.response)
        self.assertEqual(b"Hello world!", flow.text)

    def test_host_is_with_matching_pattern(self):
        flow = Flow(host="example.com")
        self.assertTrue(flow.host_is("example.com"))

    def test_host_is_with_non_matching_pattern(self):
        flow = Flow(host="example.com")
        self.assertFalse(flow.host_is("notexample.com"))

    def test_host_is_with_wildcard_match(self):
        flow = Flow(host="sub.example.com")
        self.assertTrue(flow.host_is("*.example.com"))

    def test_host_is_with_non_matching_wildcard(self):
        flow = Flow(host="example.com")
        self.assertFalse(flow.host_is("*.notexample.com"))

    def test_path_is_with_matching_pattern(self):
        request_mock = MagicMock()
        request_mock.path_is.return_value = True
        flow = Flow(request=request_mock)
        self.assertTrue(flow.path_is("/test/path"))

    def test_path_is_with_non_matching_pattern(self):
        request_mock = MagicMock()
        request_mock.path_is.return_value = False
        flow = Flow(request=request_mock)
        self.assertFalse(flow.path_is("/another/path"))

    def test_path_is_with_wildcard_match(self):
        request_mock = MagicMock()
        # Assume the mocked path_is method can handle wildcards correctly
        request_mock.path_is.side_effect = lambda pattern: pattern == "/test/*"
        flow = Flow(request=request_mock)
        self.assertTrue(flow.path_is("/test/*"))

    def test_path_is_with_non_matching_wildcard(self):
        request_mock = MagicMock()
        # Assume the mocked path_is method correctly handles non-matching patterns
        request_mock.path_is.return_value = False
        flow = Flow(request=request_mock)
        self.assertFalse(flow.path_is("/another/*"))

    def test_path_is_with_no_request(self):
        flow = Flow()  # No request is set
        self.assertFalse(flow.path_is("/test/path"))


if __name__ == "__main__":
    unittest.main()
