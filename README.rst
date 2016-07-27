Description
===========

Tagsets is a tool for performing set manipulations on tags extracted from a set
of files. The original use case was as an aid in meeting software development
process rules by searching for the presence of 'TODO', 'FIXME', etc in source
code, as well as checking that cross references match up between sets of
files. As, at it's heart, it is essentially simply a tool for defined saved
searches over a fileset, it is expected that numerous other uses can found.

Tool execution
==============

Program execution is in two stages:

1. Tag set definitions

A configuration file specifies named sets of tags, with an expression to use to
find the tags and a list of paths and filename expressions to identify where to
search.
When the tool runs, it loads the configuration file, then walks over the
filesystem to find the defined tags.

2. Tag set manipulations and output processors

In stage 2, a script is executed to perform set-type operations on the tag sets
in order to output lists or summaries either the original or the resulting tag
sets.

Tag configuration file

An example tag config file
NB. File format may still be subject to change.

.. code:: yaml

 # General config
 basepath: "/root/path/to/tagged/files"
 ignoredirs:
   - ".git"

 # Define the tag sets
 tagsets:
   - tagdefs:
       singular: definition
       plural: definitions
       regex: '[(TAG_[\w\._]+)\]'
       search:
         - file: "tagfile"

   - tagrefs:
       singular: reference
       plural: references
       # (?:...) defines a non-capturing group. Only one capturing group should exist
       # and should capture the matchable part of the tag.
       regex: '(?:ref|see)\[(TAG_[\w\._]+)\]'
       search:
         - file: "/absolute/path/to/some document/elsewhere.txt"
         - glob:
             paths:
               - "src/relative/path/to/search"
             files:
               - "*.h"
               - "*.c"

Contributing
============

I'd be glad to receive suggestions and contributions. As python is not a
language I have considerable experience with, I'd be particularly glad of
suggestions to make the code and api more pythonic.
