import unittest
import tempfile
from io import BytesIO
from collections import namedtuple
from pyscalpel.http.body.form import (
    CaseInsensitiveDict,
    MultiPartFormField,
    MultiPartForm,
    Mapping,
    cast,
    URLEncodedForm,
    JSON_KEY_TYPES,
    JSON_VALUE_TYPES,
    JSONForm,
    JSONFormSerializer,
    URLEncodedFormSerializer,
    MultiPartFormSerializer,
    multidict,
    os,
    Form,
    ObjectWithHeaders,
    convert_for_urlencode,
)


class MultiPartFormTestCase(unittest.TestCase):
    def setUp(self):
        headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="file"; filename="example.txt"',
                "Content-Type": "text/plain",
            }
        )
        content = b"This is the content of the file."
        encoding = "utf-8"
        self.form_field = MultiPartFormField(headers, content, encoding)
        self.form = MultiPartForm([self.form_field], "multipart/form-data")

    def test_mapping_interface(self):
        self.assertIsInstance(self.form, Mapping)

    def test_get_all(self):
        key = "file"
        expected_values = [self.form_field]
        values = self.form.get_all(key)
        self.assertEqual(values, expected_values)

    def test_get_all_empty_key(self):
        key = "nonexistent"
        expected_values = []
        values = self.form.get_all(key)
        self.assertEqual(values, expected_values)

    def test_get(self):
        key = "file"
        expected_value = self.form_field
        value = self.form.get(key)
        self.assertEqual(value, expected_value)

    def test_get_default(self):
        key = "nonexistent"
        default = MultiPartFormField.make("kjdsqkjdhdsqsq")
        expected_value = default
        value = self.form.get(key, default)
        self.assertEqual(value, expected_value)

    def test_del_all(self):
        key = "file"
        self.form.del_all(key)
        values = self.form.get_all(key)
        self.assertEqual(values, [])

    def test_del_all_empty_key(self):
        key = "nonexistent"
        self.form.del_all(key)  # No exception should be raised

    def test_delitem(self):
        key = "file"
        del self.form[key]
        values = self.form.get_all(key)
        self.assertEqual(values, [])

    # def test_delitem_key_error(self):
    #     key = "nonexistent"
    #     with self.assertRaises(KeyError):
    #         del self.form[key]

    def test_set(self):
        key = "new_file"
        value = MultiPartFormField.make(key)
        self.form[key] = value
        self.assertEqual(self.form.get(key), value)

    def test_set_bytes_value(self):
        key = "new_file"
        value = b"example content"
        self.form[key] = value
        form_field = cast(MultiPartFormField, self.form.get(key))
        self.assertEqual(form_field.name, key)
        self.assertEqual(form_field.content, value)

    def test_set_io_value(self):
        key = "new_file"
        value = BytesIO(b"example content")
        self.form[key] = value
        form_field = cast(MultiPartFormField, self.form.get(key))
        self.assertIsInstance(form_field, MultiPartFormField)
        self.assertEqual(form_field.name, key)
        self.assertEqual(form_field.content, b"example content")

    def test_set_none_value(self):
        key = "file"
        self.form[key] = None
        values = self.form.get_all(key)
        self.assertEqual(values, [])

    def test_set_default(self):
        key = "nonexistent"
        default = MultiPartFormField.make(key)
        value = self.form.setdefault(key, default)
        self.assertEqual(value, default)
        self.assertEqual(self.form.get(key), default)

    def test_set_default_existing(self):
        key = "file"
        default = MultiPartFormField.make(key)
        value = self.form.setdefault(key, default)
        self.assertEqual(value, self.form_field)
        self.assertEqual(self.form.get(key), self.form_field)

    def test_len(self):
        form = MultiPartForm(tuple(), "multipart/form-data; --Boundary")
        for i in range(10):
            form[str(i)] = str(i)
            self.assertEqual(i + 1, len(form))

    def test_iter(self):
        form = MultiPartForm(tuple(), "multipart/form-data; --Boundary")

        for i in range(10):
            form[str(i)] = str(i)

        expected_fields = form.fields

        # Type checker is broken and does not infer from __iter__  when converting using list()
        #   This doesn't raise any error -> fields = [field for field in form]
        fields = cast(list[MultiPartFormField], list(form))
        self.assertListEqual(fields, expected_fields)

    def test_eq_same_fields(self):
        form2 = MultiPartForm([self.form_field], "multipart/form-data")
        self.assertEqual(self.form, form2)

    def test_eq_different_fields(self):
        form2 = MultiPartForm([], "multipart/form-data")
        self.assertNotEqual(self.form, form2)

    def test_items(self):
        expected_items = [("file", self.form_field)]
        items = list(self.form.items())
        self.assertEqual(items, expected_items)

    def test_values(self):
        expected_values = [self.form_field]
        values = list(self.form.values())
        self.assertEqual(values, expected_values)

    def test_keys(self):
        expected_keys = ["file"]
        keys = list(self.form.keys())
        self.assertEqual(keys, expected_keys)

    # def test_repr(self):
    #     expected_repr = "MultiPartForm[<MultiPartFormField(headers={'Content-Disposition': 'form-data; name=\"file\"; filename=\"example.txt\"', 'Content-Type': 'text/plain'}, content=b'This is the content of the file.', encoding='utf-8')>]"
    #     form_repr = repr(self.form)
    #     self.assertEqual(form_repr, expected_repr)


class URLEncodedFormSerializerTestCase(unittest.TestCase):
    def test_serialize(self):
        serializer = URLEncodedFormSerializer()
        deserialized_body = multidict.MultiDict(((b"name", b"John"), (b"age", b"30")))
        expected = b"name=John&age=30"
        result = serializer.serialize(deserialized_body)
        self.assertEqual(result, expected)

    def test_deserialize(self):
        serializer = URLEncodedFormSerializer()
        body = b"name=John&age=30"
        expected = URLEncodedForm([(b"name", b"John"), (b"age", b"30")])
        result = serializer.deserialize(body)
        self.assertEqual(result, expected)

    def test_deserialize_empty_body(self):
        serializer = URLEncodedFormSerializer()
        body = b""
        expected = URLEncodedForm([])
        result = serializer.deserialize(body)
        self.assertEqual(result, expected)

    def test_get_empty_form(self):
        serializer = URLEncodedFormSerializer()
        expected = URLEncodedForm([])
        result = serializer.get_empty_form()
        self.assertEqual(result, expected)

    def test_deserialized_type(self):
        serializer = URLEncodedFormSerializer()
        expected = URLEncodedForm
        result = serializer.deserialized_type()
        self.assertEqual(result, expected)

    def test_import_form(self):
        exported_form = (
            ("key1", "value1"),
            ("key2", "value2"),
            ("key3", "value3"),
        )
        expected_fields = [
            (b"key1", b"value1"),
            (b"key2", b"value2"),
            (b"key3", b"value3"),
        ]
        serializer = URLEncodedFormSerializer()
        imported_form = serializer.import_form(exported_form)  # type: ignore
        self.assertIsInstance(imported_form, URLEncodedForm)
        items = list(imported_form.items())
        self.assertEqual(items, expected_fields)

    def test_export_form(self):
        form = URLEncodedForm([(b"key1", b"value1"), (b"key2", b"value2")])
        serializer = URLEncodedFormSerializer()
        exported_form = serializer.export_form(form)
        expected_exported_form = ((b"key1", b"value1"), (b"key2", b"value2"))
        self.assertEqual(exported_form, expected_exported_form)

    def test_serialize_does_urlencode(self):
        form = URLEncodedForm(
            ((b"secret", b"MySecretKey"), (b"encrypted", b"+ZSV6BfZwcr7c6m3fZTHyg=="))
        )
        serializer = URLEncodedFormSerializer()
        serialized = serializer.serialize(form)
        expected = b"secret=MySecretKey&encrypted=%2BZSV6BfZwcr7c6m3fZTHyg%3D%3D"
        self.assertEqual(expected, serialized)

    def test_setitem_with_string_key(self):
        form = URLEncodedForm([(b"key1", b"value1")])
        form["key2"] = "value2"
        self.assertEqual(form[b"key2"], b"value2")

    def test_getitem_with_string_key(self):
        form = URLEncodedForm([(b"key1", b"value1"), (b"key2", b"value2")])
        result = form["key1"]
        self.assertEqual(result, b"value1")

    def test_set_and_get_with_string_key(self):
        form = URLEncodedForm([])
        form["key1"] = "value1"
        result = form["key1"]
        self.assertEqual(result, b"value1")

    def test_import_form_with_dict(self):
        # The dictionary to be imported
        exported_dict = {
            "key1": "value1",
            "key2": "value2",
        }

        serializer = URLEncodedFormSerializer()
        imported_form = serializer.import_form(exported_dict)
        expected_fields = [(b"key1", b"value1"), (b"key2", b"value2")]

        items = list(imported_form.items())

        self.assertEqual(items, expected_fields)

    def test_import_form_skips_none_values(self):
        exported_form = (
            ("key1", "value1"),
            ("key2", None),  # This value should be skipped
            ("key3", "value3"),
        )

        serializer = URLEncodedFormSerializer()
        imported_form = serializer.import_form(exported_form)  # type: ignore

        expected_fields = [
            (b"key1", b"value1"),
            (b"key3", b"value3"),
        ]

        items = list(imported_form.items())

        self.assertEqual(items, expected_fields)

    def test_convert_for_urlencode_with_boolean(self):
        val = True
        result = convert_for_urlencode(val)
        self.assertEqual(result, "1")

        val = False
        result = convert_for_urlencode(val)
        self.assertEqual(result, "0")


class JSONFormSerializerTestCase(unittest.TestCase):
    def test_serialize(self):
        serializer = JSONFormSerializer()
        deserialized_body: dict[JSON_KEY_TYPES, JSON_VALUE_TYPES] = {
            "name": "John",
            "age": 30,
        }
        expected = b'{"name": "John", "age": 30}'
        result = serializer.serialize(deserialized_body)
        self.assertEqual(result, expected)

    def test_deserialize(self):
        serializer = JSONFormSerializer()
        body = b'{"name": "John", "age": 30}'
        expected = {"name": "John", "age": 30}
        result = serializer.deserialize(body)
        self.assertEqual(result, expected)

    def test_deserialize_empty_body(self):
        serializer = JSONFormSerializer()
        body = b""
        expected = None
        result = serializer.deserialize(body)
        self.assertEqual(result, expected)

    def test_get_empty_form(self):
        serializer = JSONFormSerializer()
        expected = JSONForm({})
        result = serializer.get_empty_form()
        self.assertEqual(result, expected)

    def test_deserialized_type(self):
        serializer = JSONFormSerializer()
        expected = JSONForm
        result = serializer.deserialized_type()
        self.assertEqual(result, expected)


class MultiPartFormFieldTestCase(unittest.TestCase):
    def test_init(self):
        headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="file"; filename="example.txt"',
                "Content-Type": "text/plain",
            }
        )
        content = b"This is the content of the file."
        encoding = "utf-8"
        expected_headers = CaseInsensitiveDict(
            {
                "Content-Disposition": 'form-data; name="file"; filename="example.txt"',
                "Content-Type": "text/plain",
            }
        )
        expected_content = b"This is the content of the file."
        expected_encoding = "utf-8"
        result = MultiPartFormField(headers, content, encoding)
        self.assertEqual(result.headers, expected_headers)
        self.assertEqual(result.content, expected_content)
        self.assertEqual(result.encoding, expected_encoding)

    def test_file_upload(self):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(b"This is the content of the file.")

        filename = temp_file.name
        content_type = "text/plain"

        form_field = MultiPartFormField.from_file(
            "file", filename, content_type=content_type
        )

        self.assertEqual(form_field.name, "file")
        self.assertEqual(form_field.filename, os.path.basename(filename))
        self.assertEqual(form_field.content_type, content_type)
        self.assertEqual(form_field.content, b"This is the content of the file.")

        os.remove(filename)


class FormConversionsTestCase(unittest.TestCase):
    def test_json_to_urlencode(self):
        json_serializer = JSONFormSerializer()
        urlencode_serializer = URLEncodedFormSerializer()

        json_form = {
            "key1": [1, 2, 3, 4, 5.0],
            "key2": "2",
            "level0": {"level1": {"level2": "nested"}},
        }

        form = JSONForm(json_form.items())

        self.assertDictEqual(json_form, form, "JSON constructor is broken")

        exported = json_serializer.export_form(form)
        expected_exported = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        self.assertTupleEqual(
            expected_exported, exported, "JSON tuple export is broken"
        )

        imported = urlencode_serializer.import_form(
            exported, cast(ObjectWithHeaders, None)
        )

        expected_fields = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        self.assertTupleEqual(
            expected_fields, imported.fields, "URLEncode import is broken"
        )

        serialized = urlencode_serializer.serialize(imported)

        expected_serialized = b"key1[]=1&key1[]=2&key1[]=3&key1[]=4&key1[]=5.0&key2=2&level0[level1][level2]=nested"

        self.assertEqual(
            expected_serialized, serialized, "Urlencode serialize is broken"
        )

    def test_urlencode_to_json_tuple(self):
        json_serializer = JSONFormSerializer()
        urlencode_serializer = URLEncodedFormSerializer()

        form = URLEncodedForm(
            [
                (b"key1[]", b"1"),
                (b"key1[]", b"2"),
                (b"key1[]", b"3"),
                (b"key1[]", b"4"),
                (b"key1[]", b"5.0"),
                (b"key2", b"2"),
                (b"level0[level1][level2]", b"nested"),
            ]
        )

        exported = urlencode_serializer.export_form(form)

        expected_exported = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        self.assertTupleEqual(
            exported,
            expected_exported,
            "Failed to export URL-encoded form to tuple",
        )

        imported = json_serializer.import_form(exported)

        expected_imported = {
            "key1": ["1", "2", "3", "4", "5.0"],
            "key2": "2",
            "level0": {"level1": {"level2": "nested"}},
        }

        self.assertDictEqual(
            imported,
            expected_imported,
            "Failed to convert URL-encoded form to JSON",
        )

    def test_urlencode_to_json_dict(self):
        json_serializer = JSONFormSerializer()
        urlencode_serializer = URLEncodedFormSerializer()

        tupled_form = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        form = URLEncodedForm(list(tupled_form))

        exported = urlencode_serializer.export_form(form)

        expected_exported = tupled_form
        self.assertTupleEqual(
            expected_exported,
            exported,
            "Failed to export URL-encoded form",
        )

        imported = json_serializer.import_form(exported)

        expected_imported = {
            "key1": ["1", "2", "3", "4", "5.0"],
            "key2": "2",
            "level0": {"level1": {"level2": "nested"}},
        }

        self.assertDictEqual(
            expected_imported,
            imported,
            "Failed to import nested values to JSON",
        )

    def test_urlencode_to_multipart(self):
        urlencode_serializer = URLEncodedFormSerializer()
        multipart_serializer = MultiPartFormSerializer()

        form = URLEncodedForm(
            [
                (b"key1[]", b"1"),
                (b"key1[]", b"2"),
                (b"key1[]", b"3"),
                (b"key1[]", b"4"),
                (b"key1[]", b"5.0"),
                (b"key2", b"2"),
                (b"level0[level1][level2]", b"nested"),
            ]
        )

        exported = urlencode_serializer.export_form(form)

        expected_exported = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        self.assertTupleEqual(exported, expected_exported)

        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )

        multipart_data = multipart_serializer.import_form(exported, req)
        multipart_bytes = bytes(multipart_data)
        expected_multipart_bytes = b"""--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
1\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
3\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
4\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
5.0\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key2"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="level0[level1][level2]"\r
\r
nested\r
--f0f056705fd4c99a5f41f9fa87c334d5--\r
\r
"""

        self.assertEqual(multipart_bytes, expected_multipart_bytes)

    def test_multipart_to_urlencoded(self):
        urlencode_serializer = URLEncodedFormSerializer()
        multipart_serializer = MultiPartFormSerializer()

        multipart_data_bytes = b"""--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1"\r
\r
1\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1"\r
\r
3\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1"\r
\r
4\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1"\r
\r
5.0\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key2"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="level0[level1][level2]"\r
\r
nested\r
--f0f056705fd4c99a5f41f9fa87c334d5--\r
\r
"""

        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )

        multipart_form = multipart_serializer.deserialize(multipart_data_bytes, req=req)

        self.assertIsNotNone(multipart_form)
        assert multipart_form

        exported = multipart_serializer.export_form(multipart_form)
        expected_exported = (
            (b"key1", b"1"),
            (b"key1", b"2"),
            (b"key1", b"3"),
            (b"key1", b"4"),
            (b"key1", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )
        self.assertTupleEqual(expected_exported, exported)

        imported = urlencode_serializer.import_form(exported, req=req)

        expected_imported = URLEncodedForm(expected_exported)

        self.assertEqual(expected_imported, imported)

        exported_urlencoded = urlencode_serializer.export_form(imported)
        expected_exported_urlencoded = expected_exported

        self.assertTupleEqual(expected_exported_urlencoded, exported_urlencoded)

    def test_multipart_to_urlencode(self):
        # Init multipart form
        multipart_bytes = b"""--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
1\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
3\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
4\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
5.0\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key2"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="level0[level1][level2]"\r
\r
nested\r
--f0f056705fd4c99a5f41f9fa87c334d5--\r
\r
"""

        multipart_form = MultiPartForm.from_bytes(
            multipart_bytes,
            "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5",
        )

        # Export form to tuple
        exported = MultiPartFormSerializer().export_form(multipart_form)
        expected_exported = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        # Ensure export works as expected
        self.assertTupleEqual(
            expected_exported, exported, "Could not export MultiPartForm"
        )

        # Convert form to URLEncoded
        imported = URLEncodedFormSerializer().import_form(exported)
        expected_imported = URLEncodedForm(expected_exported)

        self.assertTupleEqual(expected_imported.fields, imported.fields)

    def test_multipart_to_json(self):
        json_serializer = JSONFormSerializer()
        multipart_serializer = MultiPartFormSerializer()

        # Example multipart form data
        multipart_data_bytes = b"""--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
1\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
3\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
4\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
5.0\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key2"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="level0[level1][level2]"\r
\r
nested\r
--f0f056705fd4c99a5f41f9fa87c334d5--\r
\r
"""

        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )

        multipart_form = multipart_serializer.deserialize(multipart_data_bytes, req=req)

        self.assertIsNotNone(multipart_form)
        assert multipart_form

        exported = multipart_serializer.export_form(multipart_form)
        expected_exported = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        self.assertTupleEqual(expected_exported, exported)

        imported = json_serializer.import_form(exported)

        expected_imported = {
            "key1": ["1", "2", "3", "4", "5.0"],
            "key2": "2",
            "level0": {"level1": {"level2": "nested"}},
        }

        self.assertDictEqual(
            imported,
            expected_imported,
            "Failed to convert multipart form data to JSON",
        )

        exported = json_serializer.export_form(imported)

        # Should not change
        # expected_exported = (
        #     (b"key1[]", b"1"),
        #     (b"key1[]", b"2"),
        #     (b"key1[]", b"3"),
        #     (b"key1[]", b"4"),
        #     (b"key1[]", b"5.0"),
        #     (b"key2", b"2"),
        #     (b"level0[level1][level2]", b"nested"),
        # )

        self.assertTupleEqual(
            exported,
            expected_exported,
            "Failed to export JSON form to tuple",
        )

    def test_json_to_multipart(self):
        json_serializer = JSONFormSerializer()
        multipart_serializer = MultiPartFormSerializer()

        json_form = {
            "key1": [1, 2, 3, 4, 5.0],
            "key2": "2",
            "level0": {"level1": {"level2": "nested"}},
        }

        form = JSONForm(json_form.items())

        self.assertDictEqual(json_form, form, "JSON constructor is broken")

        exported = json_serializer.export_form(form)
        expected_exported = (
            (b"key1[]", b"1"),
            (b"key1[]", b"2"),
            (b"key1[]", b"3"),
            (b"key1[]", b"4"),
            (b"key1[]", b"5.0"),
            (b"key2", b"2"),
            (b"level0[level1][level2]", b"nested"),
        )

        self.assertTupleEqual(
            expected_exported, exported, "JSON tuple export is broken"
        )

        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )

        multipart_data = multipart_serializer.import_form(exported, req)
        multipart_bytes = bytes(multipart_data)
        expected_multipart_bytes = b"""--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
1\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
3\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
4\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key1[]"\r
\r
5.0\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="key2"\r
\r
2\r
--f0f056705fd4c99a5f41f9fa87c334d5\r
Content-Disposition: form-data; name="level0[level1][level2]"\r
\r
nested\r
--f0f056705fd4c99a5f41f9fa87c334d5--\r
\r
"""

        self.assertEqual(multipart_bytes, expected_multipart_bytes)

    def test_basename(self):
        content_type = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = MultiPartForm(tuple(), content_type)
        form["file"] = "hello"

        expected = "../../../../../../../../../../../../../../../etc/passwd"
        form["file"].filename = expected
        self.assertEqual(expected, form["file"].filename)

        current_file_path = __file__  # Get the path of the currently running script
        with open(current_file_path, encoding="utf-8") as file:
            form["file2"] = file

        expected = os.path.basename(current_file_path)  # Extract the file name
        self.assertEqual(expected, form["file2"].filename)

    def test_name(self):
        # Test the name property and setter
        content_type = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = MultiPartForm(tuple(), content_type)
        form["file"] = "hello"
        # Test the name property
        self.assertEqual("file", form["file"].name)
        # Test the name setter
        form["file"].name = "new_name"

        with self.assertRaises(KeyError):
            # form["file"] has been renamed to form["name"]
            print(form["file"])

        self.assertEqual("new_name", second=form["new_name"].name)

    def test_insertion(self):
        content_type = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = MultiPartForm(tuple(), content_type)
        form["file1"] = "hello"
        form["file3"] = "hello2"

        # Insert in the middle
        field = MultiPartFormField.make("file2", "hello3")
        form.insert(1, field)
        for i, field in enumerate(form):
            self.assertEqual(f"file{i + 1}", field.name)

    def test_getitem_exception(self):
        content_type = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = MultiPartForm(tuple(), content_type)
        with self.assertRaises(KeyError):
            form["nonexistent"]

    def test_set_wrong_type(self):
        content_type = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = MultiPartForm(tuple(), content_type)
        with self.assertRaises(TypeError):
            form.set("file", self)  # type:ignore

    def test_set_existing_name(self):
        content_type = (
            "multipart/form-data; boundary=----WebKitFormBoundaryy6klzjxzTk68s1dI"
        )
        form = MultiPartForm(tuple(), content_type)
        form["file"] = "hello"
        form.set("file", "hello2")
        self.assertEqual(b"hello2", form["file"].content)

    def test_serializer_import_dict(self):
        serializer = MultiPartFormSerializer()
        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )
        form = serializer.import_form({"key": "value"}, req)
        self.assertIsInstance(form, MultiPartForm)
        self.assertEqual(form["key"].content, b"value")

    def test_serializer_deserialize_garbage(self):
        serializer = MultiPartFormSerializer()
        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )
        form = serializer.deserialize(b"invalid", req)
        self.assertIsNone(form)

    def test_serializer_deserialize_empty(self):
        serializer = MultiPartFormSerializer()
        FakeRequestTp = namedtuple("FakeRequest", ["headers"])
        req = FakeRequestTp(
            headers={
                "Content-Type": "multipart/form-data; boundary=f0f056705fd4c99a5f41f9fa87c334d5"
            }
        )
        form = serializer.deserialize(b"", req)
        self.assertIsNone(form)


if __name__ == "__main__":
    unittest.main()
