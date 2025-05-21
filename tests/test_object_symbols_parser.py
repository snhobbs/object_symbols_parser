import unittest
from object_symbols_parser import combine_white_space

class TestCombineWhiteSpace(unittest.TestCase):
    def test_single_spaces(self):
        self.assertEqual(combine_white_space("Hello world"), "Hello world")

    def test_multiple_spaces(self):
        self.assertEqual(combine_white_space("Hello    world"), "Hello world")

    def test_tabs(self):
        self.assertEqual(combine_white_space("Hello\tworld"), "Hello world")

    def test_newlines(self):
        self.assertEqual(combine_white_space("Hello\nworld"), "Hello world")

    def test_mixed_whitespace(self):
        self.assertEqual(combine_white_space("Hello \t  \n world"), "Hello world")

    def test_leading_trailing_whitespace(self):
        self.assertEqual(combine_white_space("   Hello world   "), "Hello world")

    def test_empty_string(self):
        self.assertEqual(combine_white_space(""), "")

    def test_only_whitespace(self):
        self.assertEqual(combine_white_space(" \t \n  "), "")

if __name__ == "__main__":
    unittest.main()
