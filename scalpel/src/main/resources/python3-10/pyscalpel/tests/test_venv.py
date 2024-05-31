import os

# Optional because it slows downs tests by a lot and isn't much useful
if os.getenv("_VENV_TESTS"):
    import shutil
    from unittest.mock import patch
    import unittest

    from pyscalpel.venv import *

    class TestEnvironmentManager(unittest.TestCase):
        def setUp(self):
            self.venv_path = os.path.join(
                os.path.expanduser("~"), ".scalpel", "test_venv"
            )
            if os.path.exists(self.venv_path):
                shutil.rmtree(self.venv_path)
            create(self.venv_path)

        @patch("subprocess.call", return_value=0)
        def test_install(self, mock_subprocess_call):
            activate(self.venv_path)
            result = install("requests")
            pip_path = os.path.join(sys.prefix, "bin", "pip")
            mock_subprocess_call.assert_called_once_with(
                [pip_path, "install", "--require-virtualenv", "requests"]
            )
            self.assertEqual(result, 0)

        @patch("subprocess.call", return_value=0)
        def test_uninstall(self, mock_subprocess_call):
            activate(self.venv_path)
            result = uninstall("requests")
            pip_path = os.path.join(sys.prefix, "bin", "pip")
            mock_subprocess_call.assert_called_once_with(
                [pip_path, "uninstall", "--require-virtualenv", "-y", "requests"]
            )
            self.assertEqual(result, 0)

        def test_activate_deactivate(self):
            activate(self.venv_path)
            self.assertEqual(sys.prefix, os.path.abspath(self.venv_path))
            deactivate()
            self.assertEqual(sys.prefix, _old_prefix)
            self.assertEqual(sys.exec_prefix, _old_exec_prefix)

        def tearDown(self):
            if os.path.exists(self.venv_path):
                shutil.rmtree(self.venv_path)

    if __name__ == "__main__":
        unittest.main()
