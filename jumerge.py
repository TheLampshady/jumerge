#!/usr/bin/env python
from junit_tree import JUnitTestSuite

from os.path import splitext, basename
import argparse
from os import listdir
from os.path import isdir, isfile, exists
from os import makedirs
import logging
import copy


class ReportsParser(object):
    def __init__(self, reports_dir='reports'):
        self.reports_dir = reports_dir
        self.allowed_browsers = ['firefox', 'chrome', 'phantomjs']
        self.allowed_window_size = ['small', 'medium', 'large']
        self.junit_tree_list = dict()
        self.logger = setup_logger()

        allowed_stack = [self.allowed_window_size, self.allowed_browsers]
        reports = self.parse_report_directory(self.reports_dir, allowed_stack)

        file_structure = self.make_file_structure(reports)
        self.merge_reports(file_structure)

    def merge_reports(self, file_structure):
        report_type, file_list = file_structure.popitem()

        for file_path in file_list:
            class_suite_name = splitext(basename(file_path))[0]
            self.junit_tree_list[class_suite_name] = JUnitTestSuite(file_path, report_type)

        for report_type, file_list in file_structure.items():
            for file_path in file_list:
                class_suite_name = splitext(basename(file_path))[0]
                if self.junit_tree_list.get(class_suite_name):
                    self.junit_tree_list[class_suite_name].update_tree(file_path, report_type)
                else:
                    self.junit_tree_list[class_suite_name] = JUnitTestSuite(file_path, report_type)

    # TODO Make dynamic in depth
    def make_file_structure(self, reports):
        if not reports:
            return None
        file_structure = dict()
        for browser, window_list in reports.items():
            for window, file_list in window_list.items():
                file_structure[browser + '-' + window] = list()
                for report in file_list:
                    file_name = '{0}/{1}/{2}/{3}'.format(
                        self.reports_dir, browser, window, report)
                    file_structure[browser + '-' + window].append(file_name)
        return file_structure

    def parse_report_directory(self, parent_directory, valid_choice_stack):
        """
        Runs through all files and finds directories with reports
        :param parent_directory: The current directory
        :param valid_choice_stack: List of acceptable directories
        :return:
        """
        if not len(valid_choice_stack):
            return self.parse_report_file(parent_directory)

        directory_list = dict()
        valid_choices = valid_choice_stack.pop()
        for directory in listdir(parent_directory):
            if not self.is_report_directory(directory, parent_directory, valid_choices):
                continue
            child_directory = '{0}/{1}'.format(parent_directory, directory)
            directory_list[directory] = self.parse_report_directory(
                child_directory, copy.deepcopy(valid_choice_stack))
        return directory_list

    def parse_report_file(self, parent_directory):
        report_list = list()
        for report_file in listdir(parent_directory):
            report_file_path = '{0}/{1}'.format(parent_directory, report_file)
            if report_file.endswith('.xml') and isfile(report_file_path):
                report_list.append(report_file)
            else:
                self.logger.warn("File must be an xml: {0}".format(report_file_path))

        return report_list

    def is_report_directory(self, directory_name, parent_dir, valid_choices):
        directory_path = '{0}/{1}'.format(parent_dir, directory_name)

        if directory_name not in valid_choices:
            self.logger.warn("Invalid Directory: %s" % directory_name)
            return False
        if isfile(directory_path):
            self.logger.warn("You've got a loose file in your test reports {0}".format(directory_path))
            return False
        if not isdir(directory_path):
            self.logger.warn("File must be a directory: {0}".format(directory_path))
            return False

        return True

    def export_reports(self, merge_directory):
        if not exists(merge_directory):
                makedirs(merge_directory)
        self.logger.info("Records Found: %s" % len(self.junit_tree_list))
        for report_name, junit_tree in self.junit_tree_list.items():
            file_name = "%s/%s.xml" % (merge_directory, report_name)
            junit_tree.update_status()
            target = open(file_name, 'w')
            header = "<?xml version='1.0' encoding='UTF-8'?>\n"
            target.write(header)
            target.write(str(junit_tree))
            target.close()


def setup_logger():
    logger = logging.getLogger('reports parser')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)
    return logger


def main():
    parser = argparse.ArgumentParser(prog='bdd reports utility')
    parser.add_argument('-d', '--dir', default='reports', help='reports directory')
    args = parser.parse_args()
    reports_dir = args.dir

    if not exists(reports_dir) or not isdir(reports_dir):
        print "Error: Please provide a valid directory for JUnit Reports."
        return 1

    parser = ReportsParser(reports_dir)
    merge_directory = "%s/%s" % (reports_dir, 'merged')
    parser.export_reports(merge_directory)

if __name__ == "__main__":
    main()
