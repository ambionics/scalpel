import unittest
from pyscalpel.http.body.abstract import *


class TestFormSerializer(unittest.TestCase):
    def test_instantiation(self):
        class BadFormSerializer(FormSerializer):
            """FormSerializer subclass that does not implement all abstract methods"""

            pass

        with self.assertRaises(TypeError):
            BadFormSerializer()

    def test_good_implementation(self):
        class GoodFormSerializer(FormSerializer):
            """FormSerializer subclass that does implement all abstract methods"""

            def serialize(
                self, deserialized_body: Form, req: ObjectWithHeaders
            ) -> bytes: ...

            def deserialize(
                self, body: bytes, req: ObjectWithHeaders
            ) -> Form | None: ...

            def get_empty_form(self, req: ObjectWithHeaders) -> Form: ...

            def deserialized_type(self) -> type: ...

            def import_form(
                self, exported: ExportedForm, req: ObjectWithHeaders
            ) -> Form: ...

            def export_form(self, source: Form) -> TupleExportedForm: ...

        try:
            GoodFormSerializer()
        except TypeError:
            self.fail("GoodFormSerializer raised TypeError unexpectedly!")


if __name__ == "__main__":
    unittest.main()
