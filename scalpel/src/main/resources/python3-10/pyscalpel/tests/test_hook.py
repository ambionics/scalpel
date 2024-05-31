import unittest
from pyscalpel import editor


class TestHook(unittest.TestCase):
    def test_annotation(self):
        def hello():
            pass

        editor("binary")(hello)
        self.assertEqual(hello.__annotations__["scalpel_editor_mode"], "binary")

        with self.assertRaises(ValueError):
            editor("INVALID")(hello)  # type: ignore


if __name__ == "__main__":
    unittest.main()
