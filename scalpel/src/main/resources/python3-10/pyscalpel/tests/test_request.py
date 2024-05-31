from __future__ import annotations


from typing import (
    cast,
)
from pyscalpel.http.headers import Headers

from pyscalpel.http.body import (
    JSONFormSerializer,
    URLEncodedFormSerializer,
    MultiPartFormSerializer,
    MultiPartForm,
    MultiPartFormField,
    URLEncodedForm,
    JSONForm,
    json_escape_bytes,
    json_unescape_bytes,
    escape_parameter,
)

from pyscalpel.http.request import *
import unittest


class RequestGenericTestCase(unittest.TestCase):
    def test_init(self):
        method = "GET"
        scheme = "https"
        host = "example.com"
        port = 443
        path = "/path"
        http_version = "HTTP/1.1"
        headers = Headers([(b"Content-Type", b"application/json")])
        content = b'{"key": "value"}'

        request = Request(
            method=method,
            scheme=scheme,
            host=host,
            port=port,
            path=path,
            http_version=http_version,
            headers=headers,
            content=content,
            authority="",
        )

        self.assertEqual(request.method, method)
        self.assertEqual(request.scheme, scheme)
        self.assertEqual(request.host, host)
        self.assertEqual(request.port, port)
        self.assertEqual(request.path, path)
        self.assertEqual(request.http_version, http_version)
        self.assertEqual(request.headers, headers)
        self.assertEqual(request.content, content)

    def test_make(self):
        method = "POST"
        url = "http://example.com/path"
        content = '{"key": "value"}'
        headers = {
            "Content-Type": "application/json",
            "X-Custom-Header": "custom",
        }

        request = Request.make(method, url, content, headers)

        self.assertEqual(request.method, method)
        self.assertEqual(request.url, url)
        self.assertEqual(request.content, content.encode())
        self.assertEqual(request.headers.get("Content-Type"), "application/json")
        self.assertEqual(request.headers.get("X-Custom-Header"), "custom")

    def create_request(self) -> Request:
        method = "POST"
        scheme = "https"
        host = "example.com"
        port = 443
        path = "/path"
        http_version = "HTTP/1.1"
        headers = Headers(
            [
                (b"Content-Type", b"application/json; charset=utf-8"),
                (b"X-Custom-Header", b"custom"),
            ]
        )
        content = b'{"key": "value"}'

        return Request(
            method=method,
            scheme=scheme,
            host=host,
            port=port,
            path=path,
            http_version=http_version,
            headers=headers,
            content=content,
            authority="",
        )

    def test_set_url(self):
        request = Request.make("GET", "http://example.com/path")

        request.url = "https://example.com/new-path?param=value"

        self.assertEqual(request.scheme, "https")
        self.assertEqual(request.host, "example.com")
        self.assertEqual(request.port, 443)
        self.assertEqual(request.path, "/new-path?param=value")
        self.assertEqual(request.url, "https://example.com/new-path?param=value")

    def test_query_params(self):
        request = Request.make(
            "GET", "http://example.com/path?param1=value1&param2=value2"
        )

        self.assertEqual(
            request.query.get_all("param1"),
            ["value1"],
            "Failed to get query parameter 'param1'",
        )
        self.assertEqual(
            request.query.get_all("param2"),
            ["value2"],
            "Failed to get query parameter 'param2'",
        )

        request.query.set_all("param1", ["new_value1", "new_value2"])
        self.assertEqual(
            request.query.get_all("param1"),
            ["new_value1", "new_value2"],
            "Failed to set query parameter 'param1'",
        )

        request.query.add("param3", "value3")
        self.assertEqual(
            request.query.get_all("param3"),
            ["value3"],
            "Failed to add query parameter 'param3'",
        )

        # TODO: Handle remove via None, del ,remove_all
        del request.query["param2"]
        self.assertEqual(
            request.query.get_all("param2"),
            [],
            "Failed to remove query parameter 'param2'",
        )

        query_params = request.query.items()
        self.assertEqual(
            list(query_params),
            [("param1", "new_value1"), ("param3", "value3")],
            "Failed to get query parameters as items()",
        )

    def test_body_content(self):
        request = Request.make(
            "POST", "http://example.com/path", content=b"request body"
        )

        self.assertEqual(request.content, b"request body", "Failed to get request body")

        request.content = b"new content"
        self.assertEqual(request.content, b"new content", "Failed to set request body")

    def test_headers(self):
        request = Request.make(
            "GET",
            "http://example.com/path",
            headers={"Content-Type": "application/json"},
        )

        self.assertEqual(
            request.headers.get("Content-Type"),
            "application/json",
            "Failed to get header 'Content-Type'",
        )

        request.headers["Content-Type"] = "text/html"
        self.assertEqual(
            request.headers.get("Content-Type"),
            "text/html",
            "Failed to set header 'Content-Type'",
        )

        del request.headers["Content-Type"]
        self.assertIsNone(
            request.headers.get("Content-Type"),
            "Failed to delete header 'Content-Type'",
        )

    def test_http_version(self):
        request = Request.make("GET", "http://example.com/path")

        self.assertEqual(request.http_version, "HTTP/1.1", "Failed to get HTTP version")

        request.http_version = "HTTP/2.0"
        self.assertEqual(request.http_version, "HTTP/2.0", "Failed to set HTTP version")

    def test_update_serializer_from_content_type(self):
        request = self.create_request()

        # Test existing content-type
        request.update_serializer_from_content_type()
        self.assertIsInstance(request._serializer, JSONFormSerializer)

        # Test custom content-type
        request.headers["Content-Type"] = "application/x-www-form-urlencoded"
        request.update_serializer_from_content_type()
        self.assertIsInstance(request._serializer, URLEncodedFormSerializer)

        # Test unimplemented content-type
        request.headers["Content-Type"] = "application/xml"
        with self.assertRaises(FormNotParsedException):
            request.update_serializer_from_content_type()

        # Test fail_silently=True
        request.update_serializer_from_content_type(fail_silently=True)
        self.assertIsInstance(request._serializer, URLEncodedFormSerializer)

    def test_create_defaultform(self):
        request = self.create_request()

        # Test with existing form
        request.form = {"key": "value"}
        form = request.create_defaultform()
        self.assertEqual(form, {"key": "value"})
        self.assertIsInstance(request._serializer, JSONFormSerializer)

        # Test without existing form
        request.content = None
        form = request.create_defaultform()
        self.assertEqual(form, {})
        self.assertIsInstance(request._serializer, JSONFormSerializer)

        # Test unimplemented content-type
        with self.assertRaises(FormNotParsedException):
            request.update_serializer_from_content_type("application/xml")  # type: ignore

        # Test fail_silently=True
        request.create_defaultform(update_header=True)
        self.assertIsInstance(request._serializer, JSONFormSerializer)

    def test_urlencoded_form(self):
        request = self.create_request()

        # Test getter
        request._deserialized_content = URLEncodedForm([(b"key1", b"value1")])
        request.headers["Content-Type"] = "application/x-www-form-urlencoded"
        request._serializer = URLEncodedFormSerializer()
        form = request.urlencoded_form
        self.assertEqual(form, URLEncodedForm([(b"key1", b"value1")]))
        self.assertIsInstance(request._serializer, URLEncodedFormSerializer)

        # Test setter
        request.urlencoded_form = URLEncodedForm([(b"key2", b"value2")])

        # WARNING: Previous form has been invalidated
        # self.assertEqual(form, QueryParams([(b"key2", b"value2")]))

        form = request.form
        self.assertEqual(form, URLEncodedForm([(b"key2", b"value2")]))

        self.assertIsInstance(request._serializer, URLEncodedFormSerializer)

    def test_json_form(self):
        request = self.create_request()

        # Test getter
        request._deserialized_content = {"key1": "value1"}
        form = request.json_form
        self.assertEqual(form, {"key1": "value1"})
        self.assertIsInstance(request._serializer, JSONFormSerializer)

        # Test setter
        request.json_form = {"key2": "value2"}

        # WARNING: Previous form has been invalidated
        # self.assertEqual(form, {"key2": "value2"})

        form = request.form
        self.assertEqual(form, {"key2": "value2"})

        self.assertIsInstance(request._serializer, JSONFormSerializer)

    def test_multipart_form(self):
        request = self.create_request()

        # Test getter
        request.headers["Content-Type"] = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = request.multipart_form
        self.assertIsInstance(form, MultiPartForm)
        self.assertIsInstance(request._serializer, MultiPartFormSerializer)

        # Test setter
        request.multipart_form = MultiPartForm(
            (MultiPartFormField.make("key", body=b"val"),),
            content_type=request.headers["Content-Type"],
        )
        self.assertIsInstance(form, MultiPartForm)
        self.assertIsInstance(request._serializer, MultiPartFormSerializer)

    def test_multipart_complex(self):
        # Real use-case test
        request = Request.make("POST", "http://localhost:3000/upload")

        request.multipart_form["query"] = "inserer"
        self.assertEqual(request.multipart_form["query"].content, b"inserer")

        request.multipart_form["formulaireQuestionReponses[0][idQuestion]"] = 2081
        self.assertEqual(
            request.multipart_form["formulaireQuestionReponses[0][idQuestion]"].content,
            b"2081",
        )

        request.multipart_form["formulaireQuestionReponses[0][idReponse]"] = 1027
        self.assertEqual(
            request.multipart_form["formulaireQuestionReponses[0][idReponse]"].content,
            b"1027",
        )

        request.multipart_form["idQuestionnaire"] = 89
        self.assertEqual(
            request.multipart_form["idQuestionnaire"].content,
            b"89",
        )

        request.multipart_form["emptyParam"] = ""
        self.assertEqual(
            request.multipart_form["emptyParam"].content,
            b"",
        )

        from base64 import b64decode

        zip_data = b64decode(
            """UEsDBBQAAAAIAFpPvlYQIK6pcAAAACMBAAAHABwAbG9sLnBocFVUCQADu6x1ZNBwd2R1eAsAAQTo
AwAABOgDAACzsS/IKOAqSCwqTo0vLinSUM9OrTSMBhJGsSDSGEyaxEbH2mbkq+GWS63ELZmckZ+M
Uy+QNAUpykstLsGvBkiaxdqmpKYWEDIrMSc/L52gYabxhiCH5+Tkq+soqOSXlhSUlmhacxUUZeaV
xBdpIEQAUEsBAh4DFAAAAAgAWk++VhAgrqlwAAAAIwEAAAcAGAAAAAAAAQAAALSBAAAAAGxvbC5w
aHBVVAUAA7usdWR1eAsAAQToAwAABOgDAABQSwUGAAAAAAEAAQBNAAAAsQAAAAAA"""
        )

        request.multipart_form["image"] = MultiPartFormField.make(
            "image", "shell.jpg", zip_data
        )

        self.assertEqual(request.multipart_form["image"].name, "image")
        self.assertEqual(request.multipart_form["image"].filename, "shell.jpg")
        self.assertEqual(request.multipart_form["image"].content_type, "image/jpeg")
        self.assertEqual(request.multipart_form["image"].content, zip_data)
        # print("\n" + bytes(request.multipart_form).decode("latin-1"))

    def test_multipart_to_json(self):
        request = Request.make("POST", "http://localhost:3000/upload")
        request.multipart_form["query"] = "inserer"
        request.multipart_form["formulaireQuestionReponses[0][idQuestion]"] = 2081
        request.multipart_form["formulaireQuestionReponses[0][idReponse]"] = 1027
        request.multipart_form["idQuestionnaire"] = 89
        request.multipart_form["answer"] = "Hello\nWorld\n!"

        from base64 import b64decode

        zip_data = b64decode(
            """UEsDBBQAAAAIAFpPvlYQIK6pcAAAACMBAAAHABwAbG9sLnBocFVUCQADu6x1ZNBwd2R1eAsAAQTo
        AwAABOgDAACzsS/IKOAqSCwqTo0vLinSUM9OrTSMBhJGsSDSGEyaxEbH2mbkq+GWS63ELZmckZ+M
        Uy+QNAUpykstLsGvBkiaxdqmpKYWEDIrMSc/L52gYabxhiCH5+Tkq+soqOSXlhSUlmhacxUUZeaV
        xBdpIEQAUEsBAh4DFAAAAAgAWk++VhAgrqlwAAAAIwEAAAcAGAAAAAAAAQAAALSBAAAAAGxvbC5w
        aHBVVAUAA7usdWR1eAsAAQToAwAABOgDAABQSwUGAAAAAAEAAQBNAAAAsQAAAAAA"""
        )

        request.multipart_form["image"] = MultiPartFormField.make(
            "image", "shell.jpg", zip_data
        )

        # Convert form to JSON
        json_form = request.json_form
        # print("JSON_FORM:", json_form)
        self.assertEqual(json_form["query"], "inserer")
        self.assertEqual(
            json_form["formulaireQuestionReponses"]["0"]["idQuestion"], "2081"  # type: ignore
        )
        self.assertEqual(
            json_form["formulaireQuestionReponses"]["0"]["idReponse"], "1027"  # type: ignore
        )
        self.assertEqual(json_form["idQuestionnaire"], "89")
        self.assertEqual(json_form["answer"], "Hello\nWorld\n!")

        # Assert the form is converted to JSON correctly
        expected_json_form = {
            "query": "inserer",
            "formulaireQuestionReponses": {
                # - PHP arrays are actually maps, so this maps to a dict because it is the same data structure
                #   -> Even if the array keys are only int, it can map non contiguously (like having values for indexes 1,2 and 5 but not 3 and 4)
                #   -> Keys map to string because PHP would map it thay way.
                #
                # We can imagine alternate conversion mode where digit only keys would be converted to int
                # and contigous integer arrays starting from 0 would be mapped to list
                # but it could be inconsistent on many edge cases and harder to implement
                "0": {"idQuestion": "2081", "idReponse": "1027"}
            },
            "idQuestionnaire": "89",
            "image": json_escape_bytes(zip_data),
            "answer": "Hello\nWorld\n!",
        }

        # Assert that the binary data isn't destroyed
        self.assertEqual(zip_data, json_unescape_bytes(expected_json_form["image"]))

        self.assertEqual(json_form, expected_json_form)

    def test_json_to_multipart(self):
        req = Request.make("POST", "http://localhost:3000/upload")

        # Create JSON form
        req.json_form = {
            "query": "inserer",
            "formulaireQuestionReponses": {
                "0": {"idQuestion": "2081", "idReponse": "1027"}
            },
            "idQuestionnaire": "89",
            "answer": "Hello\nWorld\n!",
        }

        from base64 import b64decode

        zip_data = b64decode(
            """UEsDBBQAAAAIAFpPvlYQIK6pcAAAACMBAAAHABwAbG9sLnBocFVUCQADu6x1ZNBwd2R1eAsAAQTo
            AwAABOgDAACzsS/IKOAqSCwqTo0vLinSUM9OrTSMBhJGsSDSGEyaxEbH2mbkq+GWS63ELZmckZ+M
            Uy+QNAUpykstLsGvBkiaxdqmpKYWEDIrMSc/L52gYabxhiCH5+Tkq+soqOSXlhSUlmhacxUUZeaV
            xBdpIEQAUEsBAh4DFAAAAAgAWk++VhAgrqlwAAAAIwEAAAcAGAAAAAAAAQAAALSBAAAAAGxvbC5w
            aHBVVAUAA7usdWR1eAsAAQToAwAABOgDAABQSwUGAAAAAAEAAQBNAAAAsQAAAAAA"""
        )

        req.json_form["image"] = json_escape_bytes(zip_data)

        # Convert JSON form to multipart form
        self.assertIsInstance(req.multipart_form, MultiPartForm)

        # Check values
        self.assertEqual(req.multipart_form["query"].content, b"inserer")
        self.assertEqual(
            req.multipart_form["formulaireQuestionReponses[0][idQuestion]"].content,
            b"2081",
        )
        self.assertEqual(
            req.multipart_form["formulaireQuestionReponses[0][idReponse]"].content,
            b"1027",
        )
        self.assertEqual(req.multipart_form["idQuestionnaire"].content, b"89")
        self.assertEqual(req.multipart_form["answer"].content, b"Hello\nWorld\n!")
        self.assertEqual(req.multipart_form["image"].content, zip_data)

    def test_urlencoded_to_multipart(self):
        request = self.create_request()

        # Set urlencoded form
        request.headers["Content-Type"] = "application/x-www-form-urlencoded"
        request.urlencoded_form = URLEncodedForm(
            [(b"key1", b"value1"), (b"key2", b"value2")]
        )

        # Check urlencoded form
        self.assertEqual(
            request.urlencoded_form,
            URLEncodedForm([(b"key1", b"value1"), (b"key2", b"value2")]),
        )

        # Transform urlencoded form to multipart form
        request.headers["Content-Type"] = (
            "multipart/form-data; boundary=4N_4RB17R4RY_57R1NG"
        )
        request.update_serializer_from_content_type()

        multipart_form = request.multipart_form
        self.assertIsInstance(multipart_form, MultiPartForm)
        self.assertIsInstance(request._serializer, MultiPartFormSerializer)

        # Check multipart form
        self.assertEqual(len(multipart_form.fields), 2)
        self.assertEqual(multipart_form.fields[0].name, "key1")
        self.assertEqual(multipart_form.fields[0].content, b"value1")
        self.assertEqual(multipart_form.fields[1].name, "key2")
        self.assertEqual(multipart_form.fields[1].content, b"value2")

        # Check byte serialization
        expected_bytes = b"--4N_4RB17R4RY_57R1NG\r\n"
        expected_bytes += b'Content-Disposition: form-data; name="key1"'
        expected_bytes += b"\r\n\r\nvalue1\r\n"
        expected_bytes += b"--4N_4RB17R4RY_57R1NG\r\n"
        expected_bytes += b'Content-Disposition: form-data; name="key2"'
        expected_bytes += b"\r\n\r\nvalue2\r\n"
        expected_bytes += b"--4N_4RB17R4RY_57R1NG--\r\n\r\n"
        multipart_bytes = bytes(multipart_form)
        self.assertEqual(expected_bytes, multipart_bytes)

    def test_urlencoded_to_json(self):
        request = Request.make("GET", "http://localhost")

        # Initialize JSON form data
        request.urlencoded_form = URLEncodedForm(
            [(b"key1", b"value1"), (b"key2", b"value2")]
        )

        # Check initial form data
        form = request.urlencoded_form
        self.assertEqual(
            form, URLEncodedForm([(b"key1", b"value1"), (b"key2", b"value2")])
        )
        self.assertIsInstance(request._serializer, URLEncodedFormSerializer)

        # Convert form to JSON
        json_form = request.json_form

        # Validate the JSON form
        self.assertEqual(json_form, {"key1": "value1", "key2": "value2"})
        self.assertIsInstance(request._serializer, JSONFormSerializer)

    def test_json_to_urlencoded(self):
        request = Request.make("GET", "http://localhost")

        # Initialize JSON form data
        request.json_form = {"key1": "value1", "key2": "value2"}

        # Check initial JSON form data
        json_form = request.json_form
        self.assertEqual(json_form, {"key1": "value1", "key2": "value2"})
        self.assertIsInstance(request._serializer, JSONFormSerializer)

        # Convert JSON to URL-encoded form
        urlencoded_form = request.urlencoded_form

        # Validate the URL-encoded form
        self.assertEqual(
            urlencoded_form,
            URLEncodedForm([(b"key1", b"value1"), (b"key2", b"value2")]),
        )
        self.assertIsInstance(request._serializer, URLEncodedFormSerializer)

    def test_all_use_cases(self):
        req = Request.make(
            "GET",
            "http://localhost:3000/echo?filename=28.jpg&username=wiener&password=peter",
            headers=Headers(
                (
                    (b"X-Duplicate", b"A"),
                    (b"X-Duplicate", b"B"),
                )
            ),
        )

        # Ensure initial data is correct.
        self.assertEqual("GET", req.method)
        self.assertEqual(
            "/echo?filename=28.jpg&username=wiener&password=peter", req.path
        )
        self.assertEqual("localhost", req.host)
        self.assertEqual(3000, req.port)
        self.assertEqual("localhost:3000", req.headers["Host"])
        self.assertEqual("A, B", req.headers["X-Duplicate"])
        self.assertListEqual(["A", "B"], req.headers.get_all("X-Duplicate"))

        # Input parameters

        # Raw edit query string
        new_qs = "saucisse=poulet&chocolat=blanc#"
        req.path = req.path.split("?")[0] + "?" + new_qs
        self.assertEqual("/echo?saucisse=poulet&chocolat=blanc#", req.path)

        # Dict edit query string
        # Implemented by mitmproxy
        req.query["saucisse"] = "test123"
        self.assertDictEqual(
            {"saucisse": "test123", "chocolat": "blanc"}, dict(req.query)
        )
        expected = "/echo?saucisse=test123&chocolat=blanc"
        self.assertEqual(expected, req.path)

        req.query["saucisse"] = "123"
        req.query["number"] = 123
        req.query[4] = 123

        expected = "/echo?saucisse=123&chocolat=blanc&number=123&4=123"
        self.assertEqual(expected, req.path)

        ### SERIALISATION POST ###

        # application/x-www-form-urlencoded
        req.create_defaultform("application/x-www-form-urlencoded")
        req.urlencoded_form[b"abc"] = b"def"
        req.urlencoded_form["mark"] = "jkl"

        req.urlencoded_form[b"mark2"] = "jkl"
        req.urlencoded_form["marl3"] = "kkk"
        # req.urlencoded_form["123"] = "kkk"
        req.urlencoded_form["VACHE"] = "leet"

        req.urlencoded_form[999] = 1337

        expected = b"abc=def&mark=jkl&mark2=jkl&marl3=kkk&VACHE=leet&999=1337"
        self.assertEqual(expected, req.content)
        self.assertEqual(len(expected), req.content_length, "Wrong content-lenght")

        req.content = None
        self.assertIsNone(req.content)

        # application/json
        req.json_form[1] = "test"

        self.assertIsInstance(req._serializer, JSONFormSerializer)
        self.assertIsInstance(req.form, JSONForm)
        self.assertEqual(
            "test", req.form.get(1), f"Broken JSON form: {req._deserialized_content}"
        )

        req.json_form[1.5] = "test"

        self.assertEqual("test", req.form[1.5])

        req.json_form["test"] = 1
        req.json_form["test2"] = True
        req.json_form["test3"] = None
        req.json_form["test4"] = [1, 2, 3]
        req.json_form["test5"] = {"a": 1, "b": 2, "c": 3}

        # TODO: JSON keys should probably be converted to strings
        expected = {
            1: "test",
            1.5: "test",
            "test": 1,
            "test2": True,
            "test3": None,
            "test4": [1, 2, 3],
            "test5": {"a": 1, "b": 2, "c": 3},
        }
        self.assertDictEqual(expected, req.form)
        self.assertDictEqual(expected, req.json_form)
        expected = b'{"1": "test", "1.5": "test", "test": 1, "test2": true, "test3": null, "test4": [1, 2, 3], "test5": {"a": 1, "b": 2, "c": 3}}'
        self.assertEqual(expected, req.content)
        self.assertEqual(len(expected), req.content_length, "Wrong content-lenght")

        # multipart/form-data
        req.content = None
        req.create_defaultform("multipart/form-data ; boundary=---Boundary")

        # Ensure the Content-Type has been updated (required for multipart)
        self.assertEqual(
            "multipart/form-data ; boundary=---Boundary", req.headers["Content-Type"]
        )

        req.multipart_form["a"] = b"test default"
        req.multipart_form["file2"] = b"<html>test html</html>"
        req.multipart_form["file2"].filename = "index.html"
        req.multipart_form["file2"].content_type = "text/html"

        # Sample data to be written
        data = {"name": "John", "age": 30, "city": "New York"}

        import tempfile
        import json
        from os.path import basename
        from urllib.parse import quote

        # Create a temporary file and write some JSON to it
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix=".json"
        ) as temp:
            json.dump(data, temp)

            first_name = temp.name
            req.multipart_form["data.json"] = open(temp.name, "rb")

        # Create an empty temporary file with a malicious name
        with tempfile.NamedTemporaryFile(
            mode="w+", delete=False, suffix="sp0;0f' ed\"\\"
        ) as temp:
            second_name = temp.name
            req.multipart_form["spoofed"] = open(temp.name, "r", encoding="utf-8")

        quote = lambda param: escape_parameter(param, extended=False)

        expected = '-----Boundary\r\nContent-Disposition: form-data; name="a"\r\n\r\n'
        expected += "test default\r\n"
        expected += "-----Boundary\r\n"
        expected += (
            'Content-Disposition: form-data; name="file2"; filename="index.html"\r\n'
        )
        expected += "Content-Type: text/html\r\n\r\n<html>test html</html>\r\n"
        expected += "-----Boundary\r\n"
        expected += f'Content-Disposition: form-data; name="data.json"; filename="{basename(first_name)}"\r\n'
        expected += "Content-Type: application/json\r\n\r\n\r\n"
        expected += f'-----Boundary\r\nContent-Disposition: form-data; name="spoofed"; filename="{quote(basename(second_name))}"\r\n'
        expected += "Content-Type: application/octet-stream\r\n\r\n\r\n"
        expected += "-----Boundary--\r\n\r\n"
        expected = expected.encode("latin-1")

        self.assertEqual(expected, req.content)
        self.assertEqual(len(expected), req.content_length, "Wrong content-lenght")

        ########## Déduire la sérialisation ##########
        ############### URLENCODED ####################
        req.content = None
        req.update_serializer_from_content_type("application/x-www-form-urlencoded")
        req.create_defaultform()

        req.form["a"] = "b"
        req.form["c"] = "d"

        self.assertEqual(b"a=b&c=d", req.content)
        ########## MULTIPART ##########
        req.content = None

        req.update_serializer_from_content_type(
            "multipart/form-data; boundary=--------------------2763ba3527064667e1c4f57ca596c055"
        )
        req.create_defaultform()

        req.form[b"a"] = b"b"
        req.form[b"c"] = b"d"
        req.form[b"e"] = b"f"

        expected = b'-----Boundary\r\nContent-Disposition: form-data; name="a"'
        expected += (
            b'\r\n\r\nb\r\n-----Boundary\r\nContent-Disposition: form-data; name="c"'
        )
        expected += (
            b'\r\n\r\nd\r\n-----Boundary\r\nContent-Disposition: form-data; name="e"'
        )
        expected += b"\r\n\r\nf\r\n-----Boundary--\r\n\r\n"
        self.assertEqual(expected, req.content)
        self.assertEqual(len(expected), req.content_length, "Wrong content-lenght")

        # Set and remove the content-type
        expected = "text/html"
        req.multipart_form["a"].content_type = expected
        self.assertEqual(
            expected,
            req.multipart_form["a"].headers["Content-Type"],
            "Failed to set multipart field content-type",
        )

        req.multipart_form["a"].content_type = None
        self.assertIsNone(req.multipart_form["a"].headers.get("Content-Type"))

        # ("############# JSON ##############")

        req.content = None
        req.update_serializer_from_content_type("application/json")

        req.create_defaultform()
        req.form["a"] = "chocolat"
        req.form["b"] = 3
        req.form["c"] = True
        req.form["d"] = None
        req.form["e"] = [1, 2, 3]
        req.form["f"] = {"a": 1, "b": 2, "c": 3}

        expected = b'{"a": "chocolat", "b": 3, "c": true, "d": null, "e": [1, 2, 3], "f": {"a": 1, "b": 2, "c": 3}}'
        self.assertEqual(expected, req.content)
        req.content = None

        # Test that the seriailizer has been deducted from content-type
        req.create_defaultform("application/json")
        req.form["obj"] = {"sub1": [1, 2, 3], "sub2": 4}
        self.assertEqual(b'{"obj": {"sub1": [1, 2, 3], "sub2": 4}}', req.content)

    def test_cookies(self):
        req = Request.make("GET", "http://localhost")
        token = "f37088cde673e4741fcd30882f5ccfaf"
        req.cookies["session"] = token
        self.assertEqual(token, req.cookies["session"])
        self.assertEqual(f"session={token}", req.headers["Cookie"])
        expected = {"session": token}
        self.assertDictEqual(expected, dict(req.cookies))

        req.cookies["tracking"] = "1"
        self.assertEqual("1", req.cookies["tracking"])
        self.assertEqual(f"session={token}; tracking=1", req.headers["Cookie"])
        expected = {"session": token, "tracking": "1"}
        self.assertDictEqual(expected, dict(req.cookies))

        expected = {"hello": "world", "ambionics": "lexfo"}
        req.cookies = expected
        self.assertDictEqual(expected, dict(req.cookies))

    def test_host_header(self):
        req = Request.make("GET", "http://localhost")
        self.assertEqual("localhost", req.host_header)
        self.assertEqual(req.headers["Host"], req.host_header)

        req.host_header = "lexfo.fr"
        self.assertEqual("lexfo.fr", req.host_header)

    def test_check_param(self):
        # Easily check if a param exists
        req = Request.make("GET", "http://localhost?hello=world")
        self.assertTrue(req.query.get("hello"))
        self.assertFalse(req.query.get("absent"))

    def test_content_length(self):
        req = Request.make("GET", "http://localhost?hello=world")
        self.assertEqual(0, req.content_length)

        req.content = b"lol"
        self.assertEqual(3, req.content_length)

        with self.assertRaises(RuntimeError):
            req.content_length = 1337

        req.update_content_length = False

        req.content_length = 1337
        self.assertEqual(1337, req.content_length)

        req.content = b"Hello World"
        self.assertEqual(1337, req.content_length)

        req.update_content_length = True
        self.assertEqual(11, req.content_length)

    def test_host_is(self):
        req = Request.make("GET", "http://mail.int.google.com")

        self.assertTrue(req.host_is("mail.int.google.com"))
        self.assertTrue(req.host_is("*.google.com"))
        self.assertTrue(req.host_is("*google.com"))
        self.assertTrue(req.host_is("mail.*"))
        self.assertTrue(req.host_is("*.com"))
        self.assertTrue(req.host_is("*.*gle.*"))
        self.assertTrue(req.host_is("mail.*.*.com"))
        self.assertTrue(req.host_is("mail.*.com"))

        self.assertFalse(req.host_is("google"))
        self.assertFalse(req.host_is("mail.int.google.fr"))
        self.assertFalse(req.host_is("*.gle.*"))
        self.assertFalse(req.host_is(".com"))

    def test_urlencoded_bug(self):
        req = Request.make(
            "POST",
            "http://localhost:3000/encrypt",
            b"secret=MySecretKey&content=",
            {"Content-Type": "application/x-www-form-urlencoded"},
        )

        form = req.urlencoded_form
        self.assertIsNotNone(form)
        self.assertIsInstance(form, URLEncodedForm)
        expected = ((b"secret", b"MySecretKey"), (b"content", b""))
        self.assertTupleEqual(expected, form.fields)

    def test_form_bug(self):
        req = Request.make(
            "POST",
            "http://localhost:3000/encrypt",
            b"secret=MySecretKey&encrypted=BNTYvqs5E%2BE%2Bgx0J%2B6yCG%2FUDUChX3yf61ks%2FZeUei7k%3D",
            {"Content-Type": "application/x-www-form-urlencoded"},
        )

        form = cast(URLEncodedForm, req.form)
        self.assertIsNotNone(form)
        content_type = req.headers.get("Content-Type")
        self.assertIsNotNone(content_type)
        self.assertEqual("application/x-www-form-urlencoded", content_type)
        self.assertIsInstance(form, URLEncodedForm)
        expected = (
            (b"secret", b"MySecretKey"),
            (b"encrypted", b"BNTYvqs5E+E+gx0J+6yCG/UDUChX3yf61ks/ZeUei7k="),
        )
        self.assertTupleEqual(expected, form.fields)

    def test_content_do_not_modify_json(self):
        """
        If the user doesn't use the .json form, do not unserialize/reserialize json because it will modify whitespaces
        which might break stuff, especially in GraphQL APIS
        """
        expected = b'{"hello":"world"}'
        req = Request.make(
            "POST",
            "http://localhost:3000/graphql",
            expected,
            {"Content-Type": "application/json"},
        )
        self.assertEqual(expected, req.content)

    def test_content_do_not_modify_urlencoded(self):
        """
        If the user doesn't use the forms feature, do not unserialize/reserialize, because it might break stuff
        when the app doesnt urlencode as expected.

        Proper url encoding would be hello+world or hello%20world, but some apps may only accept the first, the second, or no encoding at all
        a generic urlencoder can not handle this cases, so the least is to not break the body on request where the content is not modified using .form features
        """
        expected = b"abc=hello world&efg=apan+yan&hij=quoi%20coubeh"
        req = Request.make(
            "POST",
            "http://localhost:3000/signup",
            expected,
            {"Content-Type": "x-www-form-urlencoded"},
        )
        self.assertEqual(expected, req.content)

    def test_path_is(self):
        req = Request.make("GET", "http://example.com/abc/def")

        self.assertTrue(req.path_is("*"))
        self.assertTrue(req.path_is("/abc/def"))
        self.assertTrue(req.path_is("/abc/*"))
        self.assertTrue(req.path_is("*/def"))
        self.assertTrue(req.path_is("*/def*"))
        self.assertTrue(req.path_is("/abc/def*"))


class TestRequestBytesMethod(unittest.TestCase):
    def test_bytes_method_basic_get_request(self):
        request = Request(
            method="GET",
            scheme="http",
            host="example.com",
            port=80,
            path="/",
            http_version="HTTP/1.1",
            headers=[(b"Host", b"example.com")],
            authority="example.com",
            content=None,
        )
        expected_bytes = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
        self.assertEqual(bytes(request), expected_bytes)

    def test_bytes_method_post_request_with_body(self):
        request = Request(
            method="POST",
            scheme="http",
            host="example.com",
            port=80,
            path="/submit",
            http_version="HTTP/1.1",
            headers=[
                (b"Host", b"example.com"),
                (b"Content-Type", b"application/x-www-form-urlencoded"),
            ],
            authority="example.com",
            content=b"key=value",
        )
        # Correctly include the Content-Length header in the expected bytes string.
        expected_bytes = b"POST /submit HTTP/1.1\r\nHost: example.com\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: 9\r\n\r\nkey=value"
        self.assertEqual(bytes(request), expected_bytes)

    def test_bytes_method_with_custom_headers(self):
        headers = Headers(
            [(b"Host", b"example.com"), (b"X-Custom-Header", b"CustomValue")]
        )
        request = Request(
            method="GET",
            scheme="http",
            host="example.com",
            port=80,
            path="/custom",
            http_version="HTTP/1.1",
            headers=headers,
            authority="example.com",
            content=None,
        )
        expected_bytes = b"GET /custom HTTP/1.1\r\nHost: example.com\r\nX-Custom-Header: CustomValue\r\n\r\n"
        self.assertEqual(bytes(request), expected_bytes)

    def test_bytes_method_http2_to_http1_conversion(self):
        # Simulate an HTTP/2 request with an :authority pseudo-header and without a Host header
        headers = Headers(
            [
                (b":authority", b"example.com"),
                (b"Content-Type", b"application/json"),
            ]
        )
        request = Request(
            method="GET",
            scheme="https",
            host="example.com",
            port=443,
            path="/",
            http_version="HTTP/2",
            headers=headers,
            authority="example.com",
            content=None,
        )
        # Expected bytes should include a Host header derived from the :authority pseudo-header,
        # and the HTTP/2 pseudo-header should be removed.
        expected_bytes = b"GET / HTTP/2\r\nHost: example.com\r\nContent-Type: application/json\r\n\r\n"
        self.assertEqual(bytes(request), expected_bytes)


class TestRequestContentType(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="GET",
            scheme="http",
            host="example.com",
            port=80,
            path="/",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=None,
        )

    def test_content_type_set_and_get(self):
        # Test setting content_type
        self.request.content_type = "application/json"
        self.assertIn("Content-Type", self.request.headers)
        self.assertEqual(self.request.headers["Content-Type"], "application/json")

        # Test getting content_type
        content_type = self.request.content_type
        self.assertEqual(content_type, "application/json")

    def test_content_type_get_when_not_set(self):
        # Ensure content_type returns None when not set
        content_type = self.request.content_type
        self.assertIsNone(content_type)


class TestRequestQuerySetter(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://example.com/path/to/resource"
        self.request = Request(
            method="GET",
            scheme="http",
            host="example.com",
            port=80,
            path="/path/to/resource",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=None,
        )

    def test_update_query_string(self):
        # Set the query string when none exists
        self.request.query = [("param1", "value1"), ("param2", "value2")]
        self.assertEqual(
            self.request.url, self.base_url + "?param1=value1&param2=value2"
        )

    def test_replace_existing_query_string(self):
        # Initialize with an existing query string
        initial_query = "initial1=val1&initial2=val2"
        self.request.url = self.base_url + "?" + initial_query
        # Replace the existing query string
        self.request.query = [("newparam1", "newvalue1"), ("newparam2", "newvalue2")]
        self.assertEqual(
            self.request.url, self.base_url + "?newparam1=newvalue1&newparam2=newvalue2"
        )

    def test_empty_query_string(self):
        # Set an empty query string
        self.request.query = []
        self.assertEqual(self.request.url, self.base_url)


class TestRequestBodyProperty(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="POST",
            scheme="http",
            host="example.com",
            port=80,
            path="/submit",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=b"initial body content",
        )

    def test_body_property_with_bytes(self):
        # Update and retrieve the body with bytes
        new_body = b"new body content"
        self.request.body = new_body
        self.assertEqual(self.request.body, new_body)  # Use the getter here
        self.assertEqual(self.request.headers["Content-Length"], str(len(new_body)))

    def test_body_property_with_str(self):
        # Update and retrieve the body with a string
        new_body_str = "new string content"
        self.request.body = new_body_str
        retrieved_body = self.request.body  # Use the getter here
        self.assertEqual(retrieved_body, new_body_str.encode())
        self.assertEqual(
            self.request.headers["Content-Length"], str(len(new_body_str.encode()))
        )

    def test_body_property_with_none(self):
        # Set the body to None and check
        self.request.body = None
        self.assertIsNone(self.request.body)  # Use the getter here
        self.assertFalse("Content-Length" in self.request.headers)


class TestRequestContentLengthProperty(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="GET",
            scheme="http",
            host="example.com",
            port=80,
            path="/",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=None,
        )

    def test_content_length_absent(self):
        # Verify content_length returns 0 when the Content-Length header is absent
        self.assertEqual(self.request.content_length, 0)

    def test_content_length_invalid(self):
        # Set the Content-Length header to a non-digit value
        self.request.update_content_length = False
        self.request.content_length = "invalid"

        extracted = self.request.headers.get("Content-Length")
        self.assertIsNotNone(extracted)
        self.assertEqual(extracted, "invalid")

        # Verify that accessing content_length raises ValueError
        with self.assertRaises(ValueError) as context:
            _ = self.request.content_length
        self.assertIn(
            "Content-Length does not contain only digits", str(context.exception)
        )


class TestRequestTextMethod(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="POST",
            scheme="http",
            host="example.com",
            port=80,
            path="/data",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=b"",
        )

    def test_text_with_no_content(self):
        # Test that text returns an empty string when content is None
        self.request.content = None
        self.assertEqual(self.request.text(), "")

    def test_text_with_default_utf8_encoding(self):
        # Test decoding with default utf-8 encoding
        self.request.content = b"\xc3\xa9"
        self.assertEqual(self.request.text(), "é")

    def test_text_with_specified_encoding(self):
        # Test decoding with a specified encoding
        self.request.content = b"\xe9"
        self.assertEqual(self.request.text(encoding="iso-8859-1"), "é")


class TestRequestCookiesSetter(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="GET",
            scheme="http",
            host="example.com",
            port=80,
            path="/",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=None,
        )

    def test_set_single_cookie(self):
        # Test setting a single cookie
        self.request.cookies = (("sessionid", "123456"),)
        self.assertEqual(self.request.headers["Cookie"], "sessionid=123456")

    def test_set_multiple_cookies(self):
        # Test setting multiple cookies
        self.request.cookies = (("sessionid", "123456"), ("userid", "abcde"))
        self.assertIn("sessionid=123456; userid=abcde", self.request.headers["Cookie"])

    def test_set_no_cookies_removes_cookie_header(self):
        # Test setting no cookies removes the Cookie header if it exists
        # Set a cookie first to ensure the header exists
        self.request.cookies = (("sessionid", "123456"),)
        self.assertTrue(self.request.headers.get("cookie"))
        # Now set no cookies and expect the Cookie header to be removed
        self.request.cookies = ()
        self.assertFalse(self.request.headers.get("cookie"))


class TestRequestCreateDefaultFormErrors(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="POST",
            scheme="http",
            host="example.com",
            port=80,
            path="/submit",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=None,
        )

    def test_create_form_with_unsupported_content_type(self):
        # Set an unsupported content type directly
        self.request.headers["Content-Type"] = "application/unsupported"
        with self.assertRaises(FormNotParsedException) as context:
            self.request.create_defaultform("application/unsupported")
        self.assertIn(
            "implemented",
            str(context.exception),
        )

    def test_create_form_with_unparsable_content_for_supported_content_type(self):
        # Set a supported content type but provide unparsable content
        self.request.headers["Content-Type"] = "application/json"
        self.request.content = b"unparsable json content"
        with self.assertRaises(FormNotParsedException) as context:
            self.request.create_defaultform("application/json")
        self.assertTrue("Could not parse content" in str(context.exception))


from requests.structures import CaseInsensitiveDict


class TestRequestMultiPartFormSetter(unittest.TestCase):
    def setUp(self):
        self.request = Request(
            method="POST",
            scheme="http",
            host="example.com",
            port=80,
            path="/upload",
            http_version="HTTP/1.1",
            headers=Headers(),
            authority="example.com",
            content=None,
        )

    def test_multipart_form_sets_content_type_header_with_field(self):
        # Create a MultiPartFormField
        field_headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="field1"',
                "Content-Type": "text/plain",
            }
        )
        field_content = b"field content"
        field = MultiPartFormField(headers=field_headers, content=field_content)

        # Assuming MultiPartForm accepts a list of MultiPartFormField objects
        multipart_form = MultiPartForm(
            fields=[field], content_type="multipart/form-data"
        )

        # Set the multipart form, triggering the setter
        self.request.multipart_form = multipart_form

        # Verify that _ensure_multipart_content_type() was called by checking the Content-Type header
        content_type_header = self.request.headers.get("Content-Type")
        self.assertTrue(
            content_type_header.startswith("multipart/form-data; boundary="),
            "Content-Type header was not set correctly for multipart/form-data.",
        )


class TestRequestEncoding(unittest.TestCase):
    def test_utf16(self):
        req_bytes = """GET / HTTP/1.1\r
Host: localhost:3000\r
X-Test: ééé\r
Content-Length: 0\r
\r
"""

        req = Request.make(
            "GET",
            "http://localhost:3000",
            headers={"Host": "localhost:3000", "X-Test": "ééé"},
        )
        new_bytes = bytes(req).decode("latin-1")
        self.assertEqual(new_bytes, req_bytes)


if __name__ == "__main__":
    unittest.main()
