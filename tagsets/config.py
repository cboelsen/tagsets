import logging
import os
import pykwalify.core
import yaml

import tagsets.filefinder

from tagsets.tagsearch import TagFileMatcher, TagTextMatcher
from tagsets.tagset import TagSet

logger = logging.getLogger(__name__)

schema_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config-schema.yaml")

class ConfBC:
    def __repr__(self):
        return "<%s at %s>(%s)" % (
            self.__class__.__name__,
            hex(id(self)),
            self.repr_detail()
        )

class SearchConf(ConfBC):
    pass

class GlobSearchConf(SearchConf):
    def __init__(self):
        self.paths = []
        self.ignoredirs = []
        self.filepatterns = []
        self.ignorepatterns = []

    def repr_detail(self):
        return "paths=%r,ignoredirs=%r,filepatterns=%r,ignorepatterns=%r" % (
            self.paths,
            self.ignoredirs,
            self.filepatterns,
            self.ignorepatterns
        )

    @classmethod
    def fromyaml(cls, glob_ng):
        logger.debug("Initialising Glob from: %r" % glob_ng)
        temp = cls()

        # add paths and files
        for path in glob_ng['paths']:
            temp.add_path(path)

        for filepattern in glob_ng['files']:
            temp.add_filepattern(filepattern)

        for dirname in glob_ng.get('ignoredirs', []):
            temp.add_ignoredir(dirname)

        for filepattern in glob_ng.get('ignore', []):
            temp.add_ignore(filepattern)

        return temp

    def add_path(self, path):
        self.paths.append(path)

    def add_filepattern(self, filepattern):
        self.filepatterns.append(filepattern)

    def add_ignoredir(self, dirname):
        self.ignoredirs.append(dirname)

    def add_ignore(self, filepattern):
        self.ignorepatterns.append(filepattern)

    def get_searchdirs(self):
        return self.paths

    def get_filematchers(self, basepath, textmatcher):
        fms = []
        for path in self.get_searchdirs():
            if not os.path.isabs(path):
                path = os.path.join(basepath, path)
            fm = TagFileMatcher(path, textmatcher)
            for ignoredir in self.ignoredirs:
                fm.add_ignored_dirname(ignoredir)
            for filepattern in self.filepatterns:
                fm.add_file_pattern(filepattern)
            for filepattern in self.ignorepatterns:
                fm.add_ignore_pattern(filepattern)
            fms.append(fm)
        return fms

class FileSearchConf(SearchConf):
    def __init__(self, filename):
        self.filename = filename

    def repr_detail(self):
        return "filename=%r" % self.filename

    def get_filematchers(self, basepath, textmatcher):
        fms = []
        if os.path.isabs(self.filename):
            path = self.filename
        else:
            path = os.path.join(basepath, self.filename)
        dirname, filename = os.path.split(path)
        fm = TagFileMatcher(dirname, textmatcher, include_subdirs = False)
        fm.add_file_pattern(filename)
        fms.append(fm)
        return fms

class TagConf(ConfBC):
    def __init__(self, name, singular, plural, regex):
        self.name     = name
        self.singular = singular
        self.plural   = plural
        self.regex    = regex
        self.searches = []

    def repr_detail(self):
        return "name=%r,singular=%r,plural=%r,regex=%r,searches=%r" % (
            self.name,
            self.singular,
            self.plural,
            self.regex,
            self.searches
        )

    @classmethod
    def fromyaml(cls, name, tagconf_ng):
        logger.debug("Initialising TagConf from: %r" % tagconf_ng)
        singular = tagconf_ng.get('singular')
        plural = tagconf_ng.get('plural')
        regex = tagconf_ng.get('regex')

        temp = cls(name, singular, plural, regex)

        searches_ng = tagconf_ng.get('search')
        for search_ng in searches_ng:
            glob_ng = search_ng.get('glob', None)
            if glob_ng is not None:
                temp.add_search(GlobSearchConf.fromyaml(glob_ng))
            else:
                file_ng = search_ng.get('file', None)
                if file_ng is not None:
                    temp.add_search(FileSearchConf(file_ng))
                else:
                    # TODO - it loks like I can get this from bad indentation in the yaml config file
                    # That didn't get caught by pykwalify because pyyaml had simply returned "None"
                    # Need to catch that circumstance better
                    logger.debug("unknown type not caught by validator. hmm.")

        return temp

    def add_search(self, search):
        self.searches.append(search)

    def get_filematchers(self, basepath):
        ttm = TagTextMatcher(self.name, self.regex)

        tfms = []
        for search in self.searches:
            tfms += search.get_filematchers(basepath, ttm)
        return tfms

class Config(ConfBC):
    def __init__(self):
        self.basepath = '/'
        self.ignoredirs = []
        self.tagconfs = {}

    def repr_detail(self):
        return "basepath=%r,ignoredirs=%r,tagconfs=%r" % (
            self.basepath,
            self.ignoredirs,
            self.tagconfs
        )

    @classmethod
    def fromyaml(cls, config_ng):
        logger.debug("Initialising Config from: %r" % config_ng)
        temp = cls()

        # TODO will want to use pwd if not given
        temp.basepath = config_ng['basepath']
        temp.ignoredirs = config_ng.get('ignoredirs', [])
        
        for tsc in config_ng['tagsets']:
            # There should actually only ever be one mapping per item in the sequence
            # but this is an easy way to code it
            for key, tagconf_ng in tsc.items():
                tagconf = TagConf.fromyaml(key, tagconf_ng)
                temp.add_tagconf(tagconf)

        return temp

    @classmethod
    def fromfile(cls, filename):
        f = open(filename, 'r')
        config_ng = yaml.safe_load(f)
        f.close()

        # Validate
        c = pykwalify.core.Core(source_data=config_ng, schema_files=[schema_file])
        c.validate()

        config = cls.fromyaml(config_ng)
        logger.info("Loaded config: %r" % config)
        return config

    def add_tagconf(self, tagconf):
        self.tagconfs[tagconf.name] = tagconf

    def build_matchers(self):
        fms = []

        for tagconf in self.tagconfs.values():
            fms += tagconf.get_filematchers(self.basepath)

        # Apply any global config
        for fm in fms:
            for dirname in self.ignoredirs:
                fm.add_ignored_dirname(dirname)

        logger.info("Built file matchers: %r" % fms)

        return fms

    def get_initial_tagsets(self):
        tss = []

        for tagconf in self.tagconfs.values():
            tss.append(TagSet(tagconf.name, tagconf.singular, tagconf.plural))

        return tss
