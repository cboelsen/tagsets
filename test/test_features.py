import os
import pytest

import tagsets.cli

from testsupport import PathGenerator, working_directory

# Path to the test files / directories
TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "feature_test_data")

pg = PathGenerator(TEST_DATA_PATH)

# Tests

def test_no_args():
    with pytest.raises(SystemExit):
        tagsets.cli.main([])

def test_list_tags(capsys):
    testdir = pg.getsubgenerator("list_tags")

    with working_directory(testdir.getroot()):
        tagsets.cli.main(['-c', testdir.getpath('config.yaml'),
                          '--list-tags'])

    out,err = capsys.readouterr()
    print("\n\n=====")
    print(out)
    print("=====\n\n")

    # Output should have a heading
    assert("tags\n====" in out)

    # Output should contain found tag (tag 'TAG-1' at line 1 in file1 in subdir1)
    assert( (testdir.getpath('subdir1/file1') + ':1 : TAG-1') in out)
