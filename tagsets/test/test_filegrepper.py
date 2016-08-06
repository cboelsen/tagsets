import os
import pytest

from tagsets.filegrepper import TextMatcher, TextMatchVisitor, grep_file
from tagsets.test.testsupport import PathGenerator

# Path to the test files / directories
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "filegrepper_test_data")

pg = PathGenerator(TEST_DATA_PATH)

# Test support code

class MatchTestVisitor(TextMatchVisitor):
    def __init__(self):
        super().__init__()
        self.matches = []

    def visit_match(self, captured_text, filename, linenumber, matcher):
        self.matches.append( (captured_text, filename, linenumber, matcher) )

# Tests

def test_grep_empty_file():
    testdir = pg.getsubgenerator("empty_file")

    tm = TextMatcher("source\[([\w-]+)\]")
    tmv = MatchTestVisitor()

    grep_file(testdir.getpath("file"),[tm],tmv)

    assert len(tmv.matches) == 0

def test_single_file_single_tag():
    testdir = pg.getsubgenerator("single_file_single_tag")

    tm = TextMatcher("source\[([\w-]+)\]")
    tmv = MatchTestVisitor()

    grep_file(testdir.getpath("file"),[tm],tmv)

    assert len(tmv.matches) == 1
    assert ("TAG1",testdir.getpath("file"),2,tm) in tmv.matches

def test_single_file_two_tagsets():
    testdir = pg.getsubgenerator("single_file_two_tagsets")

    tm1 = TextMatcher("decl\[([\w-]+)\]")
    tm2 = TextMatcher("def\[([\w-]+)\]")
    tmv = MatchTestVisitor()

    grep_file(testdir.getpath("file"),[tm1,tm2],tmv)

    assert len(tmv.matches) == 5

    # Assuming filenames are correct for this test
    assert ("A",testdir.getpath("file"),3,tm1) in tmv.matches
    assert ("B",testdir.getpath("file"),8,tm1) in tmv.matches
    assert ("C",testdir.getpath("file"),14,tm1) in tmv.matches
    assert ("A",testdir.getpath("file"),14,tm2) in tmv.matches
    assert ("C",testdir.getpath("file"),16,tm2) in tmv.matches



# Test cases to add
# =================
# multiple expressions
# multiple files
# duplicated tags
# multiple tags on line
# overlapping tags
