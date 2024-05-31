"""
Most of multipart.py is covered in test_form.py, this covers the rest, mostly the utility functions
"""

import unittest
from pyscalpel.http.body.multipart import *


class TestMultipartUtils(unittest.TestCase):
    def test_escape_parameter(self):
        self.assertEqual(escape_parameter(b'abc"def'), "abc%22def")
        self.assertEqual(escape_parameter('abc"def'), "abc%22def")
        self.assertEqual(escape_parameter('abc"def', True), "abc%22def")
        self.assertEqual(escape_parameter('abc"def', False), "abc%22def")
        self.assertEqual(escape_parameter(b'abc"def', True), "abc%22def")
        self.assertEqual(escape_parameter(b'abc"def', False), "abc%22def")
        self.assertEqual(escape_parameter('abc"def', True), "abc%22def")
        self.assertEqual(escape_parameter('abc"def', False), "abc%22def")
        self.assertEqual(escape_parameter('abc"def', True), "abc%22def")

    def test_scalar_to_bytes(self):
        self.assertEqual(scalar_to_bytes("abc"), b"abc")
        self.assertEqual(scalar_to_bytes(b"abc"), b"abc")
        self.assertEqual(scalar_to_bytes(123), b"123")
        self.assertEqual(scalar_to_bytes(123.0), b"123.0")
        self.assertEqual(scalar_to_bytes(True), b"1")
        self.assertEqual(scalar_to_bytes(False), b"0")
        # Test non scalar
        self.assertEqual(scalar_to_bytes(None), b"")
        self.assertEqual(scalar_to_bytes([1, 2, 3]), b"")
        self.assertEqual(scalar_to_bytes({"a": 1}), b"")
        self.assertEqual(scalar_to_bytes(object()), b"")

    def test_scalar_to_str(self):
        self.assertEqual(scalar_to_str("abc"), "abc")
        self.assertEqual(scalar_to_str(b"abc"), "abc")
        self.assertEqual(scalar_to_str(123), "123")
        self.assertEqual(scalar_to_str(123.0), "123.0")
        self.assertEqual(scalar_to_str(True), "1")
        self.assertEqual(scalar_to_str(False), "0")
        # Test non scalar
        self.assertEqual(scalar_to_str(None), "")
        self.assertEqual(scalar_to_str([1, 2, 3]), "")
        self.assertEqual(scalar_to_str({"a": 1}), "")
        self.assertEqual(scalar_to_str(object()), "")


class TestMultiPartFormField(unittest.TestCase):

    def test_text_method_with_empty_content(self):
        field = MultiPartFormField(CaseInsensitiveDict(), b"", "utf-8")
        self.assertEqual(field.text, "")

    def test_text_method_with_utf8_content(self):
        content = "Hello, World!".encode("utf-8")
        field = MultiPartFormField(CaseInsensitiveDict(), content, "utf-8")
        self.assertEqual(field.text, "Hello, World!")

    def test_text_method_with_iso88591_content(self):
        content = "Héllo, Wörld!".encode("iso-8859-1")
        field = MultiPartFormField(CaseInsensitiveDict(), content, "iso-8859-1")
        self.assertEqual(field.text, "Héllo, Wörld!")

    def test_text_method_with_changed_encoding(self):
        content = "Hello, World!".encode("iso-8859-1")
        field = MultiPartFormField(CaseInsensitiveDict(), content, "utf-8")
        field.encoding = "iso-8859-1"  # Change the encoding
        self.assertEqual(field.text, "Hello, World!")

    def test_bytes_method_with_name_only(self):
        headers = CaseInsensitiveDict({"Content-Disposition": 'form-data; name="test"'})
        field = MultiPartFormField(headers)
        expected_bytes = b'Content-Disposition: form-data; name="test"\r\n\r\n'
        self.assertEqual(bytes(field), expected_bytes)

    def test_bytes_method_with_content_and_type(self):
        headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="test"',
                "Content-Type": "text/plain",
            }
        )
        content = b"Hello, World!"
        field = MultiPartFormField(headers, content)
        expected_bytes = b'Content-Disposition: form-data; name="test"\r\nContent-Type: text/plain\r\n\r\nHello, World!'
        self.assertEqual(bytes(field), expected_bytes)

    def test_bytes_method_with_filename_and_content_type(self):
        headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="file"; filename="test.txt"',
                "Content-Type": "text/plain",
            }
        )
        content = b"File content"
        field = MultiPartFormField(headers, content)
        expected_bytes = b'Content-Disposition: form-data; name="file"; filename="test.txt"\r\nContent-Type: text/plain\r\n\r\nFile content'
        self.assertEqual(bytes(field), expected_bytes)

    def test_bytes_method_includes_correct_headers_and_content(self):
        headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="test"',
                "Content-Type": "text/plain",
            }
        )
        content = b"Test content"
        field = MultiPartFormField(headers, content)
        expected_start = b'Content-Disposition: form-data; name="test"\r\nContent-Type: text/plain\r\n\r\n'
        self.assertTrue(bytes(field).startswith(expected_start))
        self.assertIn(b"Test content", bytes(field))


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()
