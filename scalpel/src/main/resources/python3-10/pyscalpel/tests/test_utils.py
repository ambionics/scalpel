import unittest
from unittest.mock import patch, MagicMock
from pyscalpel.utils import (
    removeprefix,
    current_function_name,
    get_tab_name,
)  # Adjust import paths as necessary


class TestPyscalpelUtil(unittest.TestCase):
    # Tests for removeprefix
    def test_removeprefix_with_str(self):
        self.assertEqual(removeprefix("TestString", "Test"), "String")

    def test_removeprefix_with_bytes(self):
        self.assertEqual(removeprefix(b"TestBytes", b"Test"), b"Bytes")

    def test_removeprefix_no_match_str(self):
        self.assertEqual(removeprefix("TestString", "XYZ"), "TestString")

    def test_removeprefix_no_match_bytes(self):
        self.assertEqual(removeprefix(b"TestBytes", b"XYZ"), b"TestBytes")

    # Tests for current_function_name
    @patch("pyscalpel.utils.inspect.currentframe")
    def test_current_function_name(self, mock_currentframe):
        mock_currentframe.return_value = None
        self.assertEqual("", second=current_function_name())

        frame = MagicMock()
        mock_currentframe.return_value = frame

        frame.f_back = None
        self.assertEqual("", second=current_function_name())

        frame.f_back = MagicMock()
        frame.f_back.f_code.co_name = "test_function"

        self.assertEqual(current_function_name(), "test_function")

    @patch("pyscalpel.utils.inspect.currentframe")
    def test_get_tab_name_from_editor_callback(self, mock_currentframe):
        # Create a mock for the frame's code object with the desired function name
        mock_code = MagicMock()
        mock_code.co_name = "req_edit_in_test_editor"

        # Create a mock for the frame and link the mock code object
        mock_frame = MagicMock()
        mock_frame.f_code = mock_code

        # Setup the frame chain to reflect the expected call stack
        mock_frame.f_back = MagicMock()
        mock_frame.f_back.f_code = mock_code
        mock_frame.f_back.f_back = None  # End of the chain

        mock_currentframe.return_value = mock_frame

        self.assertEqual(get_tab_name(), "test_editor")

    @patch("pyscalpel.utils.inspect.currentframe")
    def test_get_tab_name_not_from_editor_callback_raises(self, mock_currentframe):
        frame = MagicMock()
        frame.f_code.co_name = "nope"
        frame.f_back = None
        mock_currentframe.return_value = frame

        with self.assertRaises(RuntimeError):
            print(get_tab_name())


if __name__ == "__main__":
    unittest.main()
