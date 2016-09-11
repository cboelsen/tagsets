import os
import pytest

from tagsets.tagsearch import TagFileMatcher, TagTextMatcher, TagMatcherVisitor
from tagsets.tagset import Tag, TagSet
from tagsets.test.testsupport import PathGenerator

# Path to the test files / directories
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "tagsearch_test_data")

pg = PathGenerator(TEST_DATA_PATH)

# Tests

def test_tagsearch():
    testdir = pg.getsubgenerator("tagsearch_test")

    defs_tm = TagTextMatcher("defs", "def\[([\w-]+)\]")
    refs_tm = TagTextMatcher("refs", "ref\[([\w-]+)\]")
    defs_fm = TagFileMatcher(pg.getroot(), defs_tm)
    refs_fm = TagFileMatcher(pg.getroot(), refs_tm)

    defs = TagSet("defs", "def", "defs")
    refs = TagSet("refs", "ref", "refs")
    tmv = TagMatcherVisitor( { "defs": defs, "refs": refs } )

    tmv.visit_file(testdir.getpath("testfile"), [defs_fm, refs_fm])

    assert defs.count() == 1
    assert refs.count() == 2
