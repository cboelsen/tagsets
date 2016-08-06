import fnmatch
import logging
import os
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)

# Defines the interface needed by the find_files function
# In most cases, it is the FileMatcher class that will be used
class FileMatcherBase(metaclass=ABCMeta):
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

    def repr_detail(self):
        return ""

    # this is guaranteed to be called for a parent directory before a child directory
    # and won't be called for a child directory if the parent directory returns False
    # Override for more specific behaviour
    @abstractmethod
    def interested_in_subdirs_of(self, path):
        raise NotImplementedError

    # this won't be called in a directory if any parent directory returns false for
    # interested_in_subdirs_of
    @abstractmethod
    def interested_in_files_in(self, path):
        raise NotImplementedError

    # TODO: pass the path as well as the filename
    @abstractmethod
    def interested_in_file(self, filename):
        raise NotImplementedError


class FileMatcher(FileMatcherBase):
    def repr_detail(self):
        return "%s, path=%r, include_subdirs=%r, ignoredirs=%r, filepatterns=%r, ignorepatterns=%r" % (
            super().repr_detail(),
            self.path,
            self.include_subdirs,
            self.ignoredirs,
            self.filepatterns,
            self.ignorepatterns
        )

    # TODO implement include_subdirs = False
    def __init__(self, path, include_subdirs = True):
        super().__init__()
        self.path = path
        self.ignoredirs = []
        self.filepatterns = []
        self.ignorepatterns = []
        self.include_subdirs = include_subdirs

    def add_file_pattern(self, filepattern):
        self.filepatterns.append(filepattern)

    def add_ignore_pattern(self, filepattern):
        self.ignorepatterns.append(filepattern)

    def add_ignored_dirname(self, dirname):
        self.ignoredirs.append(dirname)

    def interested_in_subdirs_of(self, path):
        return ( os.path.commonprefix([self.path,path]) == path or
                 ( os.path.commonprefix([self.path,path]) == self.path and
                   self.include_subdirs and
                   os.path.basename(path) not in self.ignoredirs) )

    def interested_in_files_in(self, path):
        return (os.path.commonprefix([self.path,path]) == self.path and
                os.path.basename(path) not in self.ignoredirs)

    def interested_in_file(self, filename):
        interested = False
        for pattern in self.filepatterns:
            if fnmatch.fnmatch(filename, pattern):
                interestpattern = pattern
                interested = True
        if interested:
            for pattern in self.ignorepatterns:
                if fnmatch.fnmatch(filename, pattern):
                    logger.info("%s would be interested in '%s' because it matches '%s', but has excluded it because it matches '%s'" % (self, filename, interestpattern, pattern))
                    interested = False
        if interested:
            logger.info("%s is interested in '%s' because it matches '%s'" % (self, filename, interestpattern))
        return interested

def search_paths(visitor, matchers):
    # In principal, this could walk the entire filesystem, but use of matchers enables
    # the walk to be constrained to just a sub-set

    # This is the set of active matchers
    active_matchers = set(matchers)
    # This is a stack of tuples of (<path below which there is no interest>, set of matchers)
    inactive_matchers = []
    
    for root, dirs, files in os.walk("/", followlinks=True):

        logger.info("Walking: %s" % root)

        logger.debug("  Checking whether to re-activate any matchers")
        while inactive_matchers:
            top = inactive_matchers.pop()
            if os.path.commonprefix([top[0], root]) == top[0]:
                inactive_matchers.append(top)
                break
            else:
                logger.debug("    Reactivating %s" % top[1])
                active_matchers |= top[1]

        logger.debug("  Active matchers now: %s" % active_matchers)
        logger.debug("  Inactive matchers now: %s" % inactive_matchers)

        logger.debug("  Checking for parties interested in files in the current directory")
        matchers_interested_in_files = set()
        for matcher in active_matchers:
            if matcher.interested_in_files_in(root):
                logger.debug("    %s is interested in files in %s" % (matcher, root))
                matchers_interested_in_files.add(matcher)

        if matchers_interested_in_files:
            logger.debug("  Some parties interested - walking the file list")
            for f in files:
                logger.debug("    Considering %s" % f)
                matchers_interested_in_current_file = set()
                for matcher in matchers_interested_in_files:
                    if matcher.interested_in_file(f):
                        logger.debug("      %s is interested" % matcher)
                        matchers_interested_in_current_file.add(matcher)
                if matchers_interested_in_current_file:
                    logger.debug("    interest expressed in file: %s" % f)
                    visitor.visit_file(os.path.join(root,f), matchers_interested_in_current_file)

        logger.debug("  Checking whether to deactivate any (dis-)interested parties")
        matchers_to_deactivate = set()
        for matcher in active_matchers:
            if not matcher.interested_in_subdirs_of(root):
                logger.debug("    Deactivating %r is not interested in subdirs of %s" % (matcher, root))
                matchers_to_deactivate.add(matcher)
        if matchers_to_deactivate:
            inactive_matchers.append( (root, matchers_to_deactivate) )
            active_matchers -= matchers_to_deactivate

        logger.debug("  Walking the directory list (%s)" % dirs)
        origdirs = dirs[:]
        for d in origdirs:
            logger.debug("    Considering %s" % d)
            relevant = False
            path = os.path.join(root, d)
            for matcher in active_matchers:
                if matcher.interested_in_subdirs_of(path) or matcher.interested_in_files_in(path):
                    logger.debug("    %r is interested in %s" % (matcher, path))
                    relevant = True
            if not relevant:
                dirs.remove(d)

        logger.debug("  Subdirs of interest: %r" % dirs)
        # and loop

# Base class - this acts as the glue between the search function and the interested parties
# The assumption is that the concrete subclass will understand the interested party's concrete subclass
class FileMatchVisitor(metaclass=ABCMeta):
    def __init__(self):
        pass

    @abstractmethod
    def visit_file(self, path, matchers):
        raise NotImplementedError
