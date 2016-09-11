import os
import pytest
import yaml

from tagsets.config import Config, TagConf, FileSearchConf, GlobSearchConf
from tagsets.tagsearch import TagFileMatcher, TagTextMatcher
from tagsets.test.testsupport import PathGenerator

# path to the test files / directories

TEST_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config_test_data")

pg = PathGenerator(TEST_DATA_PATH)

# Test support code

class StubTextMatcher:
    pass

# Tests

def test_config_file_does_not_exist():
    with pytest.raises(FileNotFoundError):
        Config.fromfile(pg.getpath('nonexistant-file.yaml'))

# test[req-conf-002]
def test_config_file_with_multiple_tagset_configurations():
    conf = Config.fromfile(pg.getpath('multiple-tagsets.yaml'))
    assert isinstance(conf, Config)
    assert conf.basepath == '/path'
    assert conf.ignoredirs == ['.dir_a', '.dir_b']
    assert len(conf.tagconfs) == 2
    
    ts1 = conf.tagconfs['defs']
    assert isinstance(ts1, TagConf)
    assert ts1.name == 'defs'
    assert ts1.singular == "definition"
    assert ts1.plural == "definitions"
    assert ts1.regex == 'def\[([\w-]+)\]'
    assert len(ts1.searches) == 1
    ts1_search = ts1.searches[0]
    assert isinstance(ts1_search, FileSearchConf)
    assert ts1_search.filename == "definitions.txt"
    
    ts2 = conf.tagconfs['refs']
    assert isinstance(ts2, TagConf)
    assert ts2.name == 'refs'
    assert ts2.singular == "reference"
    assert ts2.plural == "references"
    assert ts2.regex == 'ref\[([\w-]+)\]'
    assert len(ts2.searches) == 1
    ts2_search = ts2.searches[0]
    assert isinstance(ts2_search, GlobSearchConf)
    assert ts2_search.paths == ['references']
    assert ts2_search.ignoredirs == []
    assert ts2_search.filepatterns == ['*.txt']
    assert ts2_search.ignorepatterns == []

def test_file_filematcher():
    yaml_conf = {
        'basepath': 'path',
        'tagsets': [
            {'tagset': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'file': '/dir/file.txt'}],
                'regex': 'tag\\[([\\w-]+)\\]'}}
        ]}

    conf = Config.fromyaml(yaml_conf)
    matchers = conf.build_matchers()

    assert len(matchers) == 1
    fm = matchers[0]
    assert isinstance(fm, TagFileMatcher)
    # path/file matching elements tested separately
    # TODO separate out tests of ignores
    assert fm.ignoredirs == []
    assert fm.ignorepatterns == []
    tm = fm.textmatcher
    assert isinstance(tm, TagTextMatcher)
    assert tm.name == "tagset"
    assert tm.regex == "tag\\[([\\w-]+)\\]"

def test_file_relative_path():
    yaml_conf = {
        'basepath': '/path',
        'tagsets': [
            {'tagset': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'file': 'file.txt'}],
                'regex': 'tag\\[([\\w-]+)\\]'}}
        ]}

    conf = Config.fromyaml(yaml_conf)
    matchers = conf.build_matchers()

    assert len(matchers) == 1
    fm = matchers[0]
    assert fm.path == "/path"
    assert fm.filepatterns == ["file.txt"]
    assert fm.include_subdirs == False

def test_file_absolute_path():
    yaml_conf = {
        'basepath': 'path',
        'tagsets': [
            {'tagset': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'file': '/dir1/dir2/file.txt'}],
                'regex': 'tag\\[([\\w-]+)\\]'}}
        ]}

    conf = Config.fromyaml(yaml_conf)
    matchers = conf.build_matchers()

    assert len(matchers) == 1
    fm = matchers[0]
    assert fm.path == "/dir1/dir2"
    assert fm.filepatterns == ["file.txt"]
    assert fm.include_subdirs == False

def test_glob_filematcher():
    yaml_conf = {
        'basepath': '/path',
        'tagsets': [
            {'tagset': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'glob': {
                    'paths': ['.'],
                    'ignoredirs': ['dira'],
                    'files': ['*.txt'],
                    'ignore': ['file.txt']}}],
                'regex': 'tag\\[([\\w-]+)\\]'}}
        ]}

    conf = Config.fromyaml(yaml_conf)
    matchers = conf.build_matchers()

    assert len(matchers) == 1
    fm = matchers[0]
    assert isinstance(fm, TagFileMatcher)
    assert fm.path == "/path"
    assert fm.include_subdirs == True
    assert fm.ignoredirs == ['dira']
    assert fm.filepatterns == ["*.txt"]
    assert fm.ignorepatterns == ['file.txt']
    tm = fm.textmatcher
    assert isinstance(tm, TagTextMatcher)
    assert tm.name == "tagset"
    assert tm.regex == "tag\\[([\\w-]+)\\]"

def test_glob_absolute_path():
    yaml_conf = {
        'basepath': '/dira/dirb',
        'tagsets': [
            {'tagset': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'glob': {
                    'paths': ['/path'],
                    'files': ['*.txt'] }}],
                'regex': 'tag\\[([\\w-]+)\\]'}}
        ]}

    conf = Config.fromyaml(yaml_conf)
    matchers = conf.build_matchers()

    assert len(matchers) == 1
    fm = matchers[0]
    assert fm.path == "/path"
    assert fm.include_subdirs == True
    assert fm.filepatterns == ["*.txt"]

def test_global_ignoredirs():
    yaml_conf = {
        'basepath': '/path',
        'ignoredirs': ['.ignorea', 'ignoreb'],
        'tagsets': [
            {'tagset': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [
                    {'glob': {
                        'paths': ['path1'],
                        'ignoredirs': ['ignorec'],
                        'files': ['*.txt'],
                        'ignore': ['file.txt'] }},
                    {'glob': {
                        'paths': ['path2'],
                        'files': ['*.txt'],
                        'ignore': ['file.txt'] }} ],
                'regex': 'tag\\[([\\w-]+)\\]' }} ] }

    conf = Config.fromyaml(yaml_conf)
    matchers = conf.build_matchers()
    assert len(matchers) == 2

    fm1 = [ fm for fm in matchers
            if fm.path == "/path/path1" ][0]
    assert sorted(fm1.ignoredirs) == sorted(['.ignorea', 'ignoreb', 'ignorec'])

    fm2 = [ fm for fm in matchers
            if fm.path == "/path/path2" ][0]
    assert sorted(fm2.ignoredirs) == sorted(['.ignorea', 'ignoreb'])

def test_tagsets():
    yaml_conf = {
        'basepath': 'path',
        'tagsets': [{
            'set1': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'file': 'file1.txt'}],
                'regex': 'tag\\[([\\w-]+)\\]'},
            'set2': {
                'singular': 'tag',
                'plural': 'tags',
                'search': [{'file': 'file2.txt'}],
                'regex': 'tag\\[([\\w-]+)\\]'}}
        ]}

    conf = Config.fromyaml(yaml_conf)
    sets = conf.get_initial_tagsets()
    assert len(sets) == 2
    assert len([ts for ts in sets
                if ts.name == "set1"
                and ts.singular == "tag"
                and ts.plural == "tags"
                and ts.tags == []]) == 1
    assert len([ts for ts in sets
                if ts.name == "set2"
                and ts.singular == "tag"
                and ts.plural == "tags"
                and ts.tags == []]) == 1

# TODO need a lot more 'mis-configuration' tests
def test_missing_file_configuration():
    yaml_conf = yaml.load("""
basepath: "path"
tagsets:
  - tags:
      singular: "tag"
      plural: "tags"
      regex: 'ref\[([\w-]+)\]'
      search:
        - file:
""")

    conf = Config.fromyaml(yaml_conf)

 # "definitions.txt"
    
 #  # Second tagset
 #  - refs:
 #      singular: "reference"
 #      plural: "references"

 #      regex: 'ref\[([\w-]+)\]'

 #      search:
 #        - glob:
 #            paths:
 #              - "references"
 #            files:
 #              - "*.txt"
 #        - glob:
 #            paths:
 #              - "refs"
 #            files:
 #              - "*.doc"
