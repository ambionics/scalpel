import unittest

from pyscalpel.http.headers import *


class HeadersTest(unittest.TestCase):
    def setUp(self):
        self.headers = Headers(
            ((b"Host", b"example.com"), (b"Content-Type", b"application/xml"))
        )

    def test_get_header_case_insensitive(self):
        self.assertEqual(self.headers["Host"], "example.com")
        self.assertEqual(self.headers["host"], "example.com")

    def test_create_headers_from_raw_data(self):
        headers = Headers(
            [
                (b"Host", b"example.com"),
                (b"Accept", b"text/html"),
                (b"accept", b"application/xml"),
            ]
        )
        self.assertEqual(headers["Host"], "example.com")
        self.assertEqual(headers["Accept"], "text/html, application/xml")

    def test_set_header_removes_existing_headers(self):
        self.headers["Accept"] = "application/text"
        self.assertEqual(self.headers["Accept"], "application/text")

    def test_bytes_representation(self):
        expected_bytes = b"Host: example.com\r\nContent-Type: application/xml\r\n"
        self.assertEqual(bytes(self.headers), expected_bytes)

    def test_get_all(self):
        self.headers.set_all("Accept", ["text/html", "application/xml"])
        self.assertEqual(
            self.headers.get_all("Accept"), ["text/html", "application/xml"]
        )

    def test_insert(self):
        self.headers.insert(1, "User-Agent", "Mozilla/5.0")
        self.assertEqual(self.headers.fields[1], (b"User-Agent", b"Mozilla/5.0"))

        # Verify that the inserted header is accessible by name
        self.assertEqual(self.headers["User-Agent"], "Mozilla/5.0")

        # Verify that the inserted header is included in the bytes representation
        expected_bytes = b"Host: example.com\r\nUser-Agent: Mozilla/5.0\r\nContent-Type: application/xml\r\n"
        self.assertEqual(bytes(self.headers), expected_bytes)

        # Verify that inserting a header at an index greater than the length of fields appends the header
        self.headers.insert(5, "X-Custom", "Custom-Value")
        self.assertEqual(self.headers.fields[-1], (b"X-Custom", b"Custom-Value"))

        # Verify that the appended header is included in the bytes representation
        expected_bytes = b"Host: example.com\r\nUser-Agent: Mozilla/5.0\r\nContent-Type: application/xml\r\nX-Custom: Custom-Value\r\n"
        self.assertEqual(bytes(self.headers), expected_bytes)

    def test_items(self):
        self.headers["User-Agent"] = "Mozilla/5.0"
        self.headers["Accept-Language"] = "en-US,en;q=0.9"
        self.headers["Cache-Control"] = "no-cache"

        items = list(self.headers.items())
        expected_items = [
            ("Host", "example.com"),
            ("Content-Type", "application/xml"),
            ("User-Agent", "Mozilla/5.0"),
            ("Accept-Language", "en-US,en;q=0.9"),
            ("Cache-Control", "no-cache"),
        ]
        self.assertEqual(items, expected_items)

    def test_from_mitmproxy(self):
        mitmproxy_headers = Headers.from_mitmproxy(self.headers)
        self.assertEqual(mitmproxy_headers["Host"], "example.com")

    def test_encoding(self):
        head = Headers(((b"Abc", "ééé".encode("latin-1")),))
        dec = bytes(head).decode("latin-1")
        self.assertEqual("Abc: ééé\r\n", dec)


if __name__ == "__main__":
    unittest.main()
