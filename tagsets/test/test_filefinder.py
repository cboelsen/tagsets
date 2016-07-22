import logging
import os
import pytest

from tagsets.filefinder import FileMatcher, FileMatchVisitor, search_paths

# Need the path to the test files / directories
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "filefinder_test_data")

# Test support code
class FileMatchTestVisitor(FileMatchVisitor):
    def __init__(self):
        self.visitations = []

    def visit_file(self, filename, matchers):
        for m in matchers:
            self.visitations.append( (filename,m) )

class PathGenerator:
    def __init__(self, basedir):
        self.rootpath=os.path.join(TEST_DATA_PATH, basedir)

    def getpath(self, path):
        return os.path.join(self.rootpath, path)

    def getroot(self):
        return self.rootpath

def test_walk_to_single_file():
    testdir = PathGenerator("single_file")
    
    visitor = FileMatchTestVisitor()
    spi = FileMatcher(testdir.getroot(), include_subdirs = False)
    spi.add_file_pattern("file")
    
    search_paths(visitor, [spi] )
    
    assert len(visitor.visitations) == 1
    assert (testdir.getpath("file"),spi) in visitor.visitations

# Note this is a tricky test for coverage - it all depends on the order that directory entries are returned, which can't be controlled
# There may be a case for stubbing some of this
def test_exclude_subdirs_for_one_party_but_not_another():
    testdir = PathGenerator("exclude_subdirs_for_some_parties")
    
    visitor = FileMatchTestVisitor()
    spi1 = FileMatcher(testdir.getroot(), include_subdirs = True)
    spi1.add_file_pattern("file")
    spi2 = FileMatcher(testdir.getroot(), include_subdirs = True)
    spi2.add_file_pattern("file")
    spi2.add_ignored_dirname("dir2")
    
    search_paths(visitor, [spi1,spi2] )
    
    assert len(visitor.visitations) == 3
    assert (testdir.getpath("dir1/file"),spi1) in visitor.visitations
    assert (testdir.getpath("dir1/file"),spi2) in visitor.visitations
    assert (testdir.getpath("dir2/file"),spi1) in visitor.visitations

def test_ignoring_file_patterns():
    testdir=PathGenerator("ignoring_file_patterns")

    visitor = FileMatchTestVisitor()
    spi = FileMatcher(testdir.getroot(), include_subdirs = True)
    spi.add_file_pattern("file*")
    spi.add_ignore_pattern("*.doc")
    
    search_paths(visitor, [spi] )
    
    assert len(visitor.visitations) == 1
    assert (testdir.getpath("file1.txt"),spi) in visitor.visitations
