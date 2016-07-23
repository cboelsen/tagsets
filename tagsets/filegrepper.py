import logging
import re
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)

class TextMatcher(metaclass=ABCMeta):
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

    def repr_detail(self):
        return "regex=%r" % self.regex

    def __init__(self, regex):
        self.regex = regex

# TODO should eventually consider what encoding to use (option in config file?)
def grep_file(path, matchers, visitor):
    logger.info("Grepping %s with:" % path)
    for g in matchers:
        logger.info("  %r" % g)

    f = open(path, 'r')
    for linenumber,linestr in enumerate(f, start=1):
        linestr = linestr.rstrip('\n')
        logger.debug("line #%i is: %s" % (linenumber, linestr))
        for g in matchers:
            for m in re.findall(g.regex, linestr):
                logger.info("Found \"%s\" at line %i for %r" %
                            (m, linenumber, g))
                visitor.visit_match(m, path, linenumber, g)

class TextMatchVisitor(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def visit_match(self, captured_text, filename, linenumber, matcher):
        pass
