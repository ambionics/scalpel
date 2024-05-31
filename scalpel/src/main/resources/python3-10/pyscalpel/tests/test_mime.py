from pyscalpel.http.mime import *
from pyscalpel.http.body.multipart import get_mime
import unittest


class ParseMimeHeaderTestCase(unittest.TestCase):
    def test_empty_string(self):
        header_str = ""
        result = parse_mime_header_params(header_str)
        self.assertEqual(result, [])

    def test_single_pair_no_quotes(self):
        header_str = "key=value"
        result = parse_mime_header_params(header_str)
        expected = [("key", "value")]
        self.assertEqual(result, expected)

    def test_single_pair_with_quotes(self):
        header_str = 'key="value"'
        result = parse_mime_header_params(header_str)
        expected = [("key", "value")]
        self.assertEqual(result, expected)

    def test_multiple_pairs(self):
        header_str = "key1=value1; key2=value2; key3=value3"
        result = parse_mime_header_params(header_str)
        expected = [("key1", "value1"), ("key2", "value2"), ("key3", "value3")]
        self.assertEqual(result, expected)

    def test_mixed_quotes(self):
        header_str = 'key1="value1"; key2=value2; key3="value3"'
        result = parse_mime_header_params(header_str)
        expected = [("key1", "value1"), ("key2", "value2"), ("key3", "value3")]
        self.assertEqual(result, expected)

    def test_value_with_semicolon_and_quotes(self):
        header_str = 'key="value;with;semicolons"; key2=value2'
        result = parse_mime_header_params(header_str)
        expected = [("key", "value;with;semicolons"), ("key2", "value2")]
        self.assertEqual(result, expected)


class HeaderParsingTestCase(unittest.TestCase):
    def test_unparse_header_value(self):
        parsed_header = [
            ("Content-Type", "text/html"),
            ("charset", "utf-8"),
            ("boundary", "abcdef"),
        ]
        expected = 'text/html; charset="utf-8"; boundary="abcdef"'
        result = unparse_header_value(parsed_header)
        self.assertEqual(result, expected)

    def test_unparse_header_value_single_parameter(self):
        parsed_header = [
            ("Content-Type", "text/html"),
            ("charset", "utf-8"),
        ]
        expected = 'text/html; charset="utf-8"'
        result = unparse_header_value(parsed_header)
        self.assertEqual(result, expected)

    def test_parse_header(self):
        key = "Content-Type"
        value = 'text/html; charset="utf-8"; boundary="abcdef"'
        expected = [
            ("Content-Type", "text/html"),
            ("charset", "utf-8"),
            ("boundary", "abcdef"),
        ]
        result = parse_header(key, value)
        self.assertEqual(result, expected)

    def test_parse_header_single_parameter(self):
        key = "Content-Type"
        value = 'text/html; charset="utf-8"'
        expected = [
            ("Content-Type", "text/html"),
            ("charset", "utf-8"),
        ]
        result = parse_header(key, value)
        self.assertEqual(result, expected)


class BoundaryExtractionTestCase(unittest.TestCase):
    def test_extract_boundary(self):
        content_type = 'multipart/form-data; boundary="abcdefg12345"'
        encoding = "utf-8"
        expected = b"abcdefg12345"
        result = extract_boundary(content_type, encoding)
        self.assertEqual(result, expected)

    def test_extract_boundary_no_quotes(self):
        content_type = "multipart/form-data; boundary=abcdefg12345"
        encoding = "utf-8"
        expected = b"abcdefg12345"
        result = extract_boundary(content_type, encoding)
        self.assertEqual(result, expected)

    def test_extract_boundary_multiple_parameters(self):
        content_type = 'multipart/form-data; charset=utf-8; boundary="abcdefg12345"'
        encoding = "utf-8"
        expected = b"abcdefg12345"
        result = extract_boundary(content_type, encoding)
        self.assertEqual(result, expected)

    def test_extract_boundary_missing_boundary(self):
        content_type = "multipart/form-data; charset=utf-8"
        encoding = "utf-8"
        with self.assertRaisesRegex(RuntimeError, r"Missing boundary"):
            extract_boundary(content_type, encoding)

    def test_extract_boundary_unexpected_mimetype(self):
        content_type = 'application/json; boundary="abcdefg12345"'
        encoding = "utf-8"
        with self.assertRaisesRegex(RuntimeError, r"Unexpected mimetype"):
            extract_boundary(content_type, encoding)


class TestHeaderParams(unittest.TestCase):
    def setUp(self):
        self.params: Sequence[tuple[str, str | None]] = [
            ("Content-Disposition", "form-data"),
            ("name", "file"),
            ("filename", "index.html"),
        ]

    def test_find_header_param(self):
        # Testing existing key
        self.assertEqual(find_header_param(self.params, "name"), ("name", "file"))

        self.assertEqual(
            find_header_param(self.params, "filename"), ("filename", "index.html")
        )

        # Testing non-existing key
        self.assertEqual(find_header_param(self.params, "non-existing-key"), None)

    def test_update_header_param(self):
        # Testing update of existing key
        updated_params = update_header_param(self.params, "name", "updated_file")
        self.assertIn(("name", "updated_file"), updated_params)

        # Testing addition of new key
        updated_params = update_header_param(self.params, "new-key", "new-value")
        self.assertIn(("new-key", "new-value"), updated_params)

        # Testing update with None value
        updated_params = update_header_param(self.params, "name", None)
        self.assertIn(("name", None), updated_params)


class TestParseMIMEHeaderValue(unittest.TestCase):
    def test_null_string(self):
        self.assertListEqual(parse_mime_header_params(None), [])

    def test_empty_string(self):
        self.assertListEqual(parse_mime_header_params(""), [])

    def test_single_parameter(self):
        self.assertListEqual(
            parse_mime_header_params("key1=value1"), [("key1", "value1")]
        )

    def test_multiple_parameters(self):
        self.assertListEqual(
            parse_mime_header_params("key1=value1; key2=value2"),
            [("key1", "value1"), ("key2", "value2")],
        )

    def test_quoted_value(self):
        self.assertListEqual(
            parse_mime_header_params('key1="value1 with spaces"; key2=value2'),
            [("key1", "value1 with spaces"), ("key2", "value2")],
        )

    def test_extra_spaces(self):
        self.assertListEqual(
            parse_mime_header_params(' key1 = "value1 with spaces" ; key2 = value2 '),
            [("key1", "value1 with spaces"), ("key2", "value2")],
        )

    def test_value_with_equal_sign(self):
        self.assertListEqual(
            parse_mime_header_params('key1="value1=value1"; key2=value2'),
            [("key1", "value1=value1"), ("key2", "value2")],
        )

    def test_value_with_semi_colon(self):
        self.assertListEqual(
            parse_mime_header_params('key1="value1;value2"; key3=value3'),
            [("key1", "value1;value2"), ("key3", "value3")],
        )

    def test_value_with_space_at_end(self):
        self.assertListEqual(
            parse_mime_header_params('key1="value1;value2"; key3=value3    '),
            [("key1", "value1;value2"), ("key3", "value3")],
        )
        self.assertListEqual(
            parse_mime_header_params('key1="value1;value2"; key3=value3  ;  '),
            [("key1", "value1;value2"), ("key3", "value3")],
        )

    def test_parse_header(self):
        header_key = "Content-Disposition"
        header_value = 'text/html; filename="file"'
        expected = [(header_key, "text/html"), ("filename", "file")]
        parsed = parse_header(header_key, header_value)
        self.assertListEqual(expected, parsed)


# Test utils
class TestMimeUtils(unittest.TestCase):
    def test_get_mime(self):
        self.assertEqual(get_mime("file.txt"), "text/plain")
        self.assertEqual(get_mime("file.html"), "text/html")
        self.assertEqual(get_mime("file.jpg"), "image/jpeg")
        self.assertEqual(get_mime("file.png"), "image/png")
        self.assertEqual(get_mime("file.gif"), "image/gif")
        self.assertEqual(get_mime("file.pdf"), "application/pdf")
        self.assertEqual(get_mime("file.zip"), "application/zip")
        self.assertEqual(get_mime("file.tar"), "application/x-tar")

        # json
        self.assertEqual(get_mime("file.json"), "application/json")
        self.assertEqual(get_mime("file.js"), "text/javascript")

        # default
        self.assertEqual(get_mime("file"), "application/octet-stream")


if __name__ == "__main__":
    unittest.main()
