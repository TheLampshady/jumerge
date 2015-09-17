#!/usr/bin/env python

import re
from os.path import isfile, isdir
import argparse
from glob import glob


def junit_renaming(filename, suffix, mode):
    f = open(filename, 'r')
    content = f.read()
    regex_find = "<testsuite\serrors=.+name=\"(.+)\"\sskipped"

    result = re.search(regex_find, content, re.M)

    if not result:
        return None

    test_name = result.group(1)

    if mode == 's':
        name_new = str(test_name)+suffix
    elif mode == 'p':
        name_new = str(suffix) + test_name
    elif mode == 'r':
        name_new = str(suffix)

    regex_replace = "name=\"%s\"\s" % test_name

    content_new = re.sub(regex_replace, "name=\"%s\" " % name_new, content)

    f.close()
    f = open(filename, 'w')
    f.write(content_new)

    f.close()
    return


def build_path_list(path_name):
    if isfile(path_name):
        return [path_name]
    elif isdir(path_name):
        return glob(str(path_name)+'/*.xml')
    return []


def setup_parser():
    parser = argparse.ArgumentParser(description='Renames JUNIT Job Names.')
    parser.add_argument('-t', '--test', dest='test', metavar="TEST [FILE|FOLDER]",
                        type=str, required=True, default='.',
                        help='Location of tests to change.')
    parser.add_argument('-p', '--prefix', dest='prefix', metavar="STRING",
                        type=str, default=None,
                        help='Append to the front.')
    parser.add_argument('-s', '--suffix', dest='suffix', metavar="STRING",
                        type=str, default=None,
                        help='Append to back.')
    parser.add_argument('-r', '--replace', dest='replace', metavar="STRING",
                        type=str, default=None,
                        help='Replace name.')
    return parser.parse_args()


if __name__ == "__main__":
    args = setup_parser()

    path_list = build_path_list(args.test)

    for path in path_list:
        if args.prefix:
            junit_renaming(path, args.prefix, 'p')

        if args.suffix:
            junit_renaming(path, args.suffix, 's')

        if args.replace:
            junit_renaming(path, args.replace, 'r')