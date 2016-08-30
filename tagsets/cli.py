import argparse
import logging
import logging.config
import os
import yaml

import tagsets.config
import tagsets.filefinder
import tagsets.filegrepper
import tagsets.tagsearch
import tagsets.script

logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(description="Tag set manipulation and reporting utility")

    parser.add_argument('-c', '--tag-config',
                        metavar='FILE',
                        required=True,
                        help="specify which tag configuration file to use")

    parser.add_argument('-v', '--verbose',
                        action='count',
                        help="increase verbosity of output - can be used twice for extra verbosity")
    parser.add_argument('-l', '--log-config-file',
                        metavar='FILE',
                        help="Python logging configuaration file - for greater control of log output")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--list-tags',
                       action='store_true',
                       help="simply generate a summary list of all the tags found by tag set")
    group.add_argument('-s', '--run-script',
                       metavar='SCRIPT',
                       help="process the tag sets using the specified script")
    group.add_argument('-p', '--run-py-script',
                       metavar='PYSCRIPT',
                       help="process the tag sets using the specified python script")
    parser.add_argument_group()

    return parser

def configure_logging(logger_configuration_file, verbosity):
    # Set logging level
    if logger_configuration_file:
        if os.path.exists(logger_configuration_file):
            with open(logger_configuration_file, 'rt') as f:
                logconf = yaml.safe_load(f.read())
                logging.config.dictConfig(logconf)
        else:
            print("Failure loading logging configuration")
            exit(1)
    elif verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    elif verbosity == 2:
        logging.basicConfig(level=logging.DEBUG)

# Main entry point for command-line interface
def main(argv = None):
    """"CLI entry point"""

    # read command line arguments
    parser=create_parser()
    args=parser.parse_args(argv)

    configure_logging(args.log_config_file, args.verbose)
    logger.debug("arguments = " + str(args))

    # read tag configuration file
    config = tagsets.config.Config.fromfile(args.tag_config)

    # build search path tree and search for tags
    matchers = config.build_matchers()
    tss = config.get_initial_tagsets()
    tsmap = dict([ (ts.name, ts) for ts in tss ])
    grepper = tagsets.tagsearch.TagMatcherVisitor(tsmap)
    tagsets.filefinder.search_paths(grepper, matchers)

    # perform requested action
    if args.list_tags:
        for ts in tss:
            print()
            ts.print_summary()
        print()

    elif args.run_script:
        print("TODO Should run script: %s" % args.run_script)

    elif args.run_py_script:
        runner = tagsets.script.ScriptContext(tsmap)
        runner.run_python_file(args.run_py_script)

    else:
        print("Something went wrong!")
