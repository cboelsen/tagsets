import logging

logger = logging.getLogger(__name__)

class Tag():
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

    def repr_detail(self):
        return "tagstr=%r, filename=%r, linenumber=%r" % (
            self.tagstr,
            self.filename,
            self.linenumber
        )

    def __init__(self, tagstr, filename, linenumber):
        self.tagstr = tagstr
        self.filename = filename
        self.linenumber = linenumber

class TagSet():
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

    def repr_detail(self):
        return "name=%r, singular=%r, plural=%r, tags=%r" % (
            self.name,
            self.singular,
            self.plural,
            self.tags
        )

    def __init__(self, name, singular, plural):
        self.name = name
        self.singular = singular
        self.plural = plural
        self.tags = []

    def add_tag(self, tag):
        self.tags.append(tag)

    def print_summary(self):
        print(self.plural)
        print('=' * len(self.plural))
        for tag in self.tags:
            print("%s:%s : %s" % (tag.filename, tag.linenumber, tag.tagstr))

    def count(self):
        return len(self.tags)

    def contains(self, tag):
        for t in self.tags:
            if t.tagstr == tag.tagstr:
                return True
        return False

    def is_empty(self):
        return (self.count() == 0)

    # TODO There MUST be a more pythonic way to write these functions!

    def contains_no_duplicates(self):
        for t1 in self.tags:
            for t2 in self.tags:
                if t1.tagstr == t2.tagstr and t1 != t2:
                    return False
        return True

    def intersection(self, otherset):
        newset = TagSet("<calculated>", self.singular, self.plural)
        for tag in self.tags:
            if otherset.contains(tag):
                newset.add_tag(tag)
        return newset

    def minus(self, otherset):
        newset = TagSet("<calculated>", self.singular, self.plural)
        for tag in self.tags:
            if not otherset.contains(tag):
                newset.add_tag(tag)
        return newset
