""" Most JSON code is covered in test_form.py, this covers the rest """

import unittest
import pyscalpel.http.body.json_form as json_form


class TestJson(unittest.TestCase):
    def test_json_convert(self):
        data = {
            "a": 1,
            "b": "c",
            "d": [1, 2, 3],
            "e": {"f": "g"},
            "h": b"i\x00\x01\x02\x03",
        }
        expected = {
            "a": 1,
            "b": "c",
            "d": [1, 2, 3],
            "e": {"f": "g"},
            "h": "i\\u0000\\u0001\\u0002\\u0003",
        }
        self.assertEqual(json_form.json_convert(data), expected)

    # def transform_tuple_to_dict(tup):
    #     """Transforms duplicates keys to list

    #     E.g:
    #     (("key_duplicate", 1),("key_duplicate", 2),("key_duplicate", 3),
    #     ("key_duplicate", 4),("key_uniq": "val") ,
    #     ("key_duplicate", 5),("key_duplicate", 6))
    #     ->
    #     {"key_duplicate": [1,2,3,4,5], "key_uniq": "val"}

    #     Args:
    #         tup (_type_): _description_

    #     Returns:
    #         _type_: _description_
    #     """
    #     result_dict = {}
    #     for pair in tup:
    #         key, value = pair
    #         converted_key: bytes | str
    #         match key:
    #             case bytes():
    #                 converted_key = key.removesuffix(b"[]")
    #             case str():
    #                 converted_key = key.removesuffix("[]")
    #             case _:
    #                 converted_key = key

    #         if converted_key in result_dict:
    #             if isinstance(result_dict[converted_key], list):
    #                 result_dict[converted_key].append(value)
    #             else:
    #                 result_dict[converted_key] = [result_dict[converted_key], value]
    #         else:
    #             result_dict[converted_key] = value
    #     return result_dict

    def test_transform_tuple_to_dict(self):
        data = (
            ("key_duplicate", 1),
            ("key_duplicate", 2),
            ("key_duplicate", 3),
            ("key_duplicate", 4),
            ("key_uniq", "val"),
            ("key_duplicate", 5),
            ("key_duplicate", 6),
        )
        expected = {
            "key_duplicate": [1, 2, 3, 4, 5, 6],
            "key_uniq": "val",
        }
        self.assertEqual(json_form.transform_tuple_to_dict(data), expected)

        #         match key:
        #             case bytes():
        #                 converted_key = key.removesuffix(b"[]")
        #             case str():
        #                 converted_key = key.removesuffix("[]")
        #             case _:
        #                 converted_key = key
        # Also cover bytes and _ cases
        data = (
            (b"key_duplicate[]", 1),
            (b"key_duplicate[]", 2),
            (b"key_duplicate[]", 3),
            (b"key_duplicate[]", 4),
            (b"key_uniq", "val"),
            (b"key_duplicate[]", 5),
            (b"key_duplicate[]", 6),
            (1, 2),
        )

        expected = {
            b"key_duplicate": [1, 2, 3, 4, 5, 6],
            b"key_uniq": "val",
            1: 2,
        }
        self.assertEqual(json_form.transform_tuple_to_dict(data), expected)
