import copy
import pytest

from tagsets.tagset import Tag, TagSet

# Test support code

def assert_tagset_contents_eq(lhs, rhs):
    rhstags = copy.deepcopy(rhs.tags)
    for lt in lhs.tags:
        item_removed_from_rhscopy = False
        for rt in rhstags:
            if (lt.tagstr == rt.tagstr and
                lt.filename == rt.filename and
                lt.linenumber == rt.linenumber):
                rhstags.remove(rt)
                item_removed_from_rhscopy = True
                break # out of inner loop
        assert item_removed_from_rhscopy, "All items in lhs set are present in rhs set"
    assert not rhstags, "All items in rhs set are present in lhs set"

def assert_tagsets_eq(lhs, rhs):
    assert lhs.name == rhs.name
    assert lhs.singular == rhs.singular
    assert lhs.plural == rhs.plural
    assert_tagset_contents_eq(lhs, rhs)

# Tests

def test_tag_properties():
    tag = Tag("tag string", "/a/file/path", 13)

    assert tag.tagstr == "tag string"
    assert tag.filename == "/a/file/path"
    assert tag.linenumber == 13

def test_set_membership():
    tag1 = Tag("tag1", "tag source", 1)
    tag2 = Tag("tag2", "tag source", 2)
    tag1_equivalent = Tag("tag1", "other tag source", 3)
    tset = TagSet("test", "test tag", "test tags")

    tset.add_tag(tag1)
    tset.add_tag(tag2)
    assert tset.contains(tag1)
    assert tset.contains(tag2)

    # Tag set membership is defined by the tag string, not identity
    assert tag1 != tag1_equivalent
    assert tset.contains(tag1_equivalent)

def test_set_size():
    tag1 = Tag("tag1", "tag source", 1)
    tag2 = Tag("tag2", "tag source", 2)
    tag1_equivalent = Tag("tag1", "other tag source", 3)
    tset = TagSet("test", "test tag", "test tags")

    assert tset.count() == 0
    tset.add_tag(tag1)
    assert tset.count() == 1
    tset.add_tag(tag2)
    assert tset.count() == 2
    # Tag admission to a set is based on identity, not properties
    tset.add_tag(tag1_equivalent)
    assert tset.count() == 3

def test_set_emptiness():
    tag = Tag("tag", "tag source", 1)
    tset = TagSet("test", "test tag", "test tags")

    assert tset.is_empty()
    tset.add_tag(tag)
    assert tset.count() == 1
    assert not tset.is_empty()

def test_set_print_summary(capsys):
    tag1 = Tag("tag1", "tag source", 1)
    tag2 = Tag("tag2", "tag source", 2)
    tset = TagSet("test", "test tag", "test tags")

    tset.add_tag(tag1)
    tset.add_tag(tag2)

    tset.print_summary()
    out,err = capsys.readouterr()
    assert out == "test tags\n=========\ntag source:1 : tag1\ntag source:2 : tag2\n"

def test_set_contains_duplicates():
    tag1 = Tag("tag1", "tag source", 1)
    tag2 = Tag("tag2", "tag source", 2)
    tag1_equivalent = Tag("tag1", "other tag source", 3)
    tset = TagSet("test", "test tag", "test tags")

    tset.add_tag(tag1)
    tset.add_tag(tag2)
    tset.add_tag(tag1_equivalent)

    assert not tset.contains_no_duplicates()

def test_set_contains_no_duplicates():
    tag1 = Tag("tag1", "tag source", 1)
    tag2 = Tag("tag2", "tag source", 1)
    tag3 = Tag("tag3", "other tag source", 1)
    tset = TagSet("test", "test tag", "test tags")

    tset.add_tag(tag1)
    tset.add_tag(tag2)
    tset.add_tag(tag3)

    assert tset.contains_no_duplicates()

def test_set_intersection():
    set1_tag1 = Tag("tag1", "defs", 1)
    set1_tag2 = Tag("tag2", "defs", 2)
    set1_tag3 = Tag("tag3", "defs", 3)
    set1_tag4 = Tag("tag4", "defs", 4)
    tset1 = TagSet("defs", "definition", "definitions")
    tset1.add_tag(set1_tag1)
    tset1.add_tag(set1_tag2)
    tset1.add_tag(set1_tag3)
    tset1.add_tag(set1_tag4)
    
    set2_tag2 = Tag("tag2", "refs", 2)
    set2_tag3 = Tag("tag3", "refs", 3)
    set2_tag5 = Tag("tag5", "refs", 5)
    tset2 = TagSet("refs", "reference", "references")
    tset2.add_tag(set2_tag2)
    tset2.add_tag(set2_tag3)
    tset2.add_tag(set2_tag5)

    orig_tset1 = copy.deepcopy(tset1)
    orig_tset2 = copy.deepcopy(tset2)

    tset1_intersection_tset2 = tset1.intersection(tset2)
    assert tset1_intersection_tset2.name == "<calculated>"
    assert tset1_intersection_tset2.singular == "definition"
    assert tset1_intersection_tset2.plural == "definitions"
    assert tset1_intersection_tset2.count() == 2
    assert tset1_intersection_tset2.contains(set1_tag2)
    assert tset1_intersection_tset2.contains(set1_tag3)

    # Original sets are unmodified
    assert_tagsets_eq(tset1, orig_tset1)
    assert_tagsets_eq(tset2, orig_tset2)

def test_set_minus():
    set1_tag1 = Tag("tag1", "defs", 1)
    set1_tag2 = Tag("tag2", "defs", 2)
    set1_tag3 = Tag("tag3", "defs", 3)
    set1_tag4 = Tag("tag4", "defs", 4)
    tset1 = TagSet("defs", "definition", "definitions")
    tset1.add_tag(set1_tag1)
    tset1.add_tag(set1_tag2)
    tset1.add_tag(set1_tag3)
    tset1.add_tag(set1_tag4)
    
    set2_tag2 = Tag("tag2", "refs", 2)
    set2_tag3 = Tag("tag3", "refs", 3)
    set2_tag5 = Tag("tag5", "refs", 5)
    tset2 = TagSet("refs", "reference", "references")
    tset2.add_tag(set2_tag2)
    tset2.add_tag(set2_tag3)
    tset2.add_tag(set2_tag5)

    orig_tset1 = copy.deepcopy(tset1)
    orig_tset2 = copy.deepcopy(tset2)

    tset1_minus_tset2 = tset1.minus(tset2)
    assert tset1_minus_tset2.name == "<calculated>"
    assert tset1_minus_tset2.singular == "definition"
    assert tset1_minus_tset2.plural == "definitions"
    assert tset1_minus_tset2.count() == 2
    assert tset1_minus_tset2.contains(set1_tag1)
    assert tset1_minus_tset2.contains(set1_tag4)

    # Original sets are unmodified
    assert_tagsets_eq(tset1, orig_tset1)
    assert_tagsets_eq(tset2, orig_tset2)
