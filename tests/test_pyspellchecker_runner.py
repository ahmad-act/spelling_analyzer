import unittest
import tempfile
import os
from unittest.mock import patch
from src.CodeReview.pyspellchecker_runner import run_pyspellchecker

class TestSpellcheckerRunner(unittest.TestCase):

    def _create_temp_file(self, content):
        tmp = tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False)
        tmp.write(content)
        tmp.flush()
        tmp.close()
        self.addCleanup(lambda: os.path.exists(tmp.name) and os.unlink(tmp.name))
        return tmp.name

    def test_detects_misspelled_words_in_comments_and_strings(self):
        content = (
            "# This commmentt has missspelled words\n"
            "x = 'spleling erorr'\n"
            "y = \"anothr errr here\"\n"
            "z = '''multi\nline\nstrng with eror'''\n"
        )
        file_path = self._create_temp_file(content)
        result = run_pyspellchecker(file_path)
        words = [issue["word"] for issue in result if "word" in issue]

        self.assertIn("commmentt", words)
        self.assertIn("missspelled", words)
        self.assertIn("spleling", words)
        self.assertIn("erorr", words)
        self.assertIn("anothr", words)
        self.assertIn("errr", words)
        self.assertIn("strng", words)
        self.assertIn("eror", words)

        # Check that source is correctly identified as comment or code
        for issue in result:
            self.assertIn(issue["source"], ("comment", "code"))

    def test_no_false_positives_on_correct_spelling(self):
        content = (
            "# This comment has no mistakes\n"
            "x = 'correct string here'\n"
        )
        file_path = self._create_temp_file(content)
        result = run_pyspellchecker(file_path)
        self.assertEqual(result, [])

    def test_empty_file_returns_empty_list(self):
        file_path = self._create_temp_file("")
        result = run_pyspellchecker(file_path)
        self.assertEqual(result, [])

    def test_handles_file_read_error(self):
        # Patch open to raise an IOError
        with patch("builtins.open", side_effect=IOError("Cannot open file")):
            result = run_pyspellchecker("fake_path.py")
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), 1)
            self.assertIn("error", result[0])
            self.assertIn("Cannot open file", result[0]["error"])

    def test_handles_line_processing_exceptions_gracefully(self):
        # Patch re.search to raise an error to simulate bad regex behavior
        def fake_search(*args, **kwargs):
            raise Exception("regex failure")
        file_path = self._create_temp_file("# comment\nx = 'string'\n")
        with patch("re.search", side_effect=fake_search):
            result = run_pyspellchecker(file_path)
            # Should log errors and append error dict for each line where failure occurred
            errors = [issue for issue in result if "error" in issue]
            self.assertTrue(len(errors) > 0)

    def test_multiple_string_literals_on_line(self):
        content = (
            "a = 'misspeled' + \"errored\"  # commmentt\n"
        )
        file_path = self._create_temp_file(content)
        result = run_pyspellchecker(file_path)
        words = [issue["word"] for issue in result if "word" in issue]

        self.assertIn("misspeled", words)
        self.assertIn("errored", words)
        self.assertIn("commmentt", words)

    def test_multiline_string_literal(self):
        # Multiline string literal with misspelled words
        content = (
            's = """\n'
            'this is a multline\n'
            'strng with eror\n'
            '"""\n'
        )
        file_path = self._create_temp_file(content)
        result = run_pyspellchecker(file_path)
        words = [issue["word"] for issue in result if "word" in issue]
        self.assertIn("multline", words)
        self.assertIn("strng", words)
        self.assertIn("eror", words)

if __name__ == '__main__':
    unittest.main()
