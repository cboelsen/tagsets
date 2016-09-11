import tagsets.tagset
import tagsets.filefinder
import tagsets.filegrepper

from tagsets.filegrepper import grep_file

class TagFileMatcher(tagsets.filefinder.FileMatcher):
    def repr_detail(self):
        return "%s, textmatcher=%r" % (
            super().repr_detail(),
            self.textmatcher
        )

    def __init__(self, path, textmatcher, include_subdirs = True):
        super().__init__(path, include_subdirs)
        self.textmatcher = textmatcher

class TagTextMatcher(tagsets.filegrepper.TextMatcher):
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

    def repr_detail(self):
        return "%r, %r" % (self.name, self.regex)

    def __init__(self, name, regex):
        super().__init__(regex)
        self.name = name

class TagMatcherVisitor(tagsets.filefinder.FileMatchVisitor,
                        tagsets.filegrepper.TextMatchVisitor):
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

    def repr_detail(self):
        return "%r" % self.tsmap

    def __init__(self, tsmap):
        self.tsmap = tsmap

    def visit_file(self, filename, filematchers):
        textmatchers = set()
        for filematcher in filematchers:
            textmatchers.add(filematcher.textmatcher)
        grep_file(filename, textmatchers, self)

    def visit_match(self, captured_text, filename, linenumber, matcher):
        t = tagsets.tagset.Tag(captured_text, filename, linenumber)
        self.tsmap[matcher.name].add_tag(t)

# TODO - I should probably consider recording paths relative to some specified base path

