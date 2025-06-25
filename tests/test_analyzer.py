# tests/test_analyzer.py

import unittest
import tempfile
import os
from unittest.mock import patch
from src.CodeAnalyzer.analyzer import analyze_file, analyze_project

TEST_PY = 'test.py'
TEST_JS = 'test.js'


class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory with test files
        self.test_dir = tempfile.TemporaryDirectory()
        self.py_file = os.path.join(self.test_dir.name, TEST_PY)
        self.js_file = os.path.join(self.test_dir.name, TEST_JS)

        with open(self.py_file, 'w', encoding='utf-8') as f:
            f.write("# commmentt with a speling error\n")
            f.write("s = 'strng with errr'\n")

        with open(self.js_file, 'w', encoding='utf-8') as f:
            f.write("// commmentt in js\n")
            f.write("var str = 'eror in string';\n")

    def tearDown(self):
        self.test_dir.cleanup()

    def test_analyze_file_returns_dict(self):
        result = analyze_file(self.py_file)
        self.assertIsInstance(result, dict)
        self.assertIn("pyspellchecker", result)

    def test_analyze_file_missing_file(self):
        result = analyze_file("non_existent_file.py")
        self.assertIn("error", result)
        self.assertIn("File not found", result["error"])

    def test_analyze_file_spellchecker_failure(self):
        with patch("src.CodeAnalyzer.analyzer.run_pyspellchecker", side_effect=Exception("tool crash")):
            result = analyze_file(self.py_file)
            self.assertIn("pyspellchecker", result)
            self.assertIn("error", result["pyspellchecker"])
            self.assertIn("tool crash", result["pyspellchecker"]["error"])

    def test_analyze_project_detects_multiple_files(self):
        report = analyze_project(self.test_dir.name)
        self.assertIn(TEST_PY, report)
        self.assertIn(TEST_JS, report)
        self.assertIsInstance(report[TEST_PY], dict)

    def test_analyze_project_ignores_unsupported_files(self):
        txt_file = os.path.join(self.test_dir.name, "README.txt")
        with open(txt_file, 'w') as f:
            f.write("This should not be analyzed.")
        report = analyze_project(self.test_dir.name)
        self.assertNotIn("README.txt", report)

    def test_analyze_project_empty_directory(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            report = analyze_project(empty_dir)
            self.assertEqual(report, {})

    def test_analyze_project_invalid_path(self):
        result = analyze_project("non_existent_directory")
        self.assertIn("error", result)
        self.assertIn("not a directory", result["error"])

    def test_analyze_project_nested_files(self):
        nested_dir = os.path.join(self.test_dir.name, "nested")
        os.makedirs(nested_dir)
        nested_file = os.path.join(nested_dir, TEST_PY)
        with open(nested_file, 'w', encoding='utf-8') as f:
            f.write("print('hello')\n")
        report = analyze_project(self.test_dir.name)
        self.assertIn(os.path.join("nested", TEST_PY), report)


if __name__ == '__main__':
    unittest.main()
