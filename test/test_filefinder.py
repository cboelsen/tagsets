import os
import pytest

from tagsets.filefinder import FileMatcher, FileMatchVisitor, search_paths
from testsupport import PathGenerator

# TODO look into whether a fixture would be appropriate for the pathgenerator

# Path to the test files / directories
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "filefinder_test_data")

pg = PathGenerator(TEST_DATA_PATH)

# Test support code

class FileMatchTestVisitor(FileMatchVisitor):
    def __init__(self):
        super().__init__()
        self.visitations = []

    def visit_file(self, filename, matchers):
        for m in matchers:
            self.visitations.append( (filename,m) )

# Tests

def test_walk_to_single_file():
    testdir = pg.getsubgenerator("single_file")
    
    visitor = FileMatchTestVisitor()
    matcher = FileMatcher(testdir.getroot(), include_subdirs = False)
    matcher.add_file_pattern("file")
    
    search_paths(visitor, [matcher] )
    
    assert len(visitor.visitations) == 1
    assert (testdir.getpath("file"),matcher) in visitor.visitations

# Note this is a tricky test for coverage - it all depends on the order that directory entries are returned, which can't be controlled
# TODO There may be a case for stubbing some of this
def test_exclude_subdirs_for_one_party_but_not_another():
    testdir = pg.getsubgenerator("exclude_subdirs_for_some_parties")
    
    visitor = FileMatchTestVisitor()
    matcher1 = FileMatcher(testdir.getroot(), include_subdirs = True)
    matcher1.add_file_pattern("file")
    matcher2 = FileMatcher(testdir.getroot(), include_subdirs = True)
    matcher2.add_file_pattern("file")
    matcher2.add_ignored_dirname("dir2")
    
    search_paths(visitor, [matcher1,matcher2] )
    
    assert len(visitor.visitations) == 3
    assert (testdir.getpath("dir1/file"),matcher1) in visitor.visitations
    assert (testdir.getpath("dir1/file"),matcher2) in visitor.visitations
    assert (testdir.getpath("dir2/file"),matcher1) in visitor.visitations

def test_ignoring_file_patterns():
    testdir=pg.getsubgenerator("ignoring_file_patterns")

    visitor = FileMatchTestVisitor()
    matcher = FileMatcher(testdir.getroot(), include_subdirs = True)
    matcher.add_file_pattern("file*")
    matcher.add_ignore_pattern("*.doc")
    
    search_paths(visitor, [matcher] )
    
    assert len(visitor.visitations) == 1
    assert (testdir.getpath("file1.txt"),matcher) in visitor.visitations
