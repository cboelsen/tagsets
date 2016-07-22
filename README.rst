The idea is to create a tool for performing set manipulations on tags
extracted from a set of files. The intention is to use these to check for
traceability between various documents.

Configuration will consist of two parts:

1. Tag set definitions

This will specify a name for a set of tags, provide an expression to use to
find the tags and list paths and filename expressions to identify where to
search.

2. Tag set manipulations and output processors

This will use a simple syntax to perform set-type operations on the tag sets
and to output lists or summaries of either the original or the resulting tag
sets

An example syntax.

This is not set in stone, but I'd like to get to something like the following:

tag set definitions:

-----------------------------
- requirements:

    # do I need these?
    plural: "requirements"
    singular: "requirement"

    # The entire expression must be matched to identify a tag
    # The capture group (defined in brackets) is part that is used as the name
    # of the tag within the set to uniqueness recorded in the set
    # This finds a string of the form "req[A-TAG-12]" and records a tag named "A-TAG-12"
    regex: "req\[([\w-]+)\]"

    # Paths to search for the tags
    paths:
        - "./docs/requirements"

    # Files with the identified paths to search for tags
    files:
        - "*.txt"
        - "*.html"

- implementation:
    reqex: "impl\[([\w-]+)\]"
    paths:
        - "./src"
    files:
        - "*.c"
        - "*.h"

- tests:
    reqex: "test\[([\w-]+)\]"
    paths:
        - "./tests"
    files:
        - "*.c"    # many tests are defined by automated test code
        - "*.h"
        - "*.txt"
-------------------------

Tag set manipulation script:

-------------------------
# Calculate set relations
define reqs_with_impl (intersection requirements implementation)
define reqs_with_no_impl (difference requirements implementation)
define impl_with_no_req (difference implementation requirements)
define reqs_with_tests (intersection requirements tests)
define reqs_with_no_test (difference requirements tests)
define tests_with_no_req (difference tests requirements)

# Output tag counts
print "Tag counts"
print "Number of requirements tags : %s" (count requirements)
print "Number of implementation tags : %s" (count implementation)
print "Number of test tags : %s" (count tests)
print

# Check tag rules
print "Checking rules"
require "All requirements must be unique" (no_duplicates_in requirements)
require "All requirements must be implemented" (is_empty reqs_with_no_impl)
require "All requirements must be tested" (is_empty reqs_with_no_test)
require "All implementation must map to a requirement" (is_empty impl_with_no_req)
require "All tests must map to a requirement" (is_empty tests_with_no_req)
require "There mustn't be multiple tests for the same requirement" (no_duplicates_in tests)
print

# Report completeness
define perc_impled (div (count reqs_with_impl) (count requirements))
define perc_tested (div (count reqs_with_tests) (count requirements))
print "Implementation coverage of requirements : %s" perc_impled
print "Test coverage of requirements : %s" perc_tested
print

# Output reports
print "Generating requirements reports"
output to "requirements-list.html" html_list requirements
output to "requirements-with-no-implementation.txt" list reqs_with_no_impl
output to "requirements-implementation-traceability.html" html_matrix requirements implementation
output to "requirements-with-no-test.txt" list reqs_with_no_test
output to "requirements-tests-traceability.html" html_matrix requirements tests
print

print_result
-------------------------

And an example output might be something like:

-------------------------
$ tagset -c tag-config.yaml -s tag-operations
Searching for tags .. done
Running script 'tag-operations':

Tag counts
Number of requirements tags : 85
Number of implementation tags : 112
Number of test tags : 35

Checking rules
All requirements must be unique : pass
All requirements must be implemented : pass
All requirements must be tested : FAIL
All implementation must map to a requirement : FAIL
All tests must map to a requirement : pass
There mustn't be multiple tests for the same requirement : pass

Implementation coverage of requirements : 100%
Test coverage of requirements : 41%

Generating requirements reports

Overall outcome : FAIL

$ echo $?
1
$
-------------------------

Thoughts:

The test script; should I make it entirely lisp. Or all python maybe?
