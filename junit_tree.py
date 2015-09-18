import re
import xml.etree.ElementTree as ET
#from lxml import etree as ET


class JUnitTestSuite(object):
    root = None

    def __init__(self, file_path, report_type):
        self.step_name = 'name'
        self.status = 'status'
        self.failure_message = 'message'
        self.split_char = ' | '

        #parser = ET.XMLParser(strip_cdata=False)
        #tree = ET.parse(file_path, parser)
        tree = ET.parse(file_path)
        self.root = tree.getroot()

        self.add_new_title(report_type)

    def __str__(self):
        result = ET.tostring(self.root, 'utf-8')
        result = re.sub(r'&lt;!\[CDATA\[', '<![CDATA[', result)
        result = re.sub(r']]\\&gt;', ']]>', result)
        return result

    def __repr__(self):
        return str(self)

    def add_new_title(self, test_type):
        for index, child in enumerate(self.root):
            class_name = child.attrib.get('classname')
            class_name += self.split_char
            class_name += test_type
            self.root[index].attrib['classname'] = class_name

    def add_title(self, test_type, add_child):
        found = False
        for index, child in enumerate(self.root):

            if self.is_same_element(child, add_child):
                class_name = child.attrib.get('classname') + self.split_char + test_type
                self.root[index].attrib['classname'] = class_name
                found = True

        if not found:
            class_name = add_child.attrib.get('classname')
            class_name += self.split_char
            class_name += test_type

            add_child.attrib['classname'] = class_name
            self.root.append(add_child)

    def add_cdata(self):
        cdata_format = "\n<![CDATA[\n%s\n]]\>\n"
        for child in self.root:
            content_tag = child.find('failure')
            if content_tag is not None:
                content_tag.text = cdata_format % content_tag.text.strip()

            content_tag = child.find('error')
            if content_tag is not None:
                content_tag.text = cdata_format % content_tag.text.strip()

            content_tag = child.find('system-out')
            if content_tag is not None:
                content_tag.text = cdata_format % content_tag.text.strip()

    def is_same_element(self, node1, node2):
        if node1.attrib.get(self.step_name) == node2.attrib.get(self.step_name):
            if node1.attrib.get(self.status) == node2.attrib.get(self.status):

                if node1.attrib.get(self.status) != 'failed':
                    return True
                try:
                    failure1 = node1.find('failure')
                    if failure1 is not None:
                        failure1 = node1.find('error')
                    failure2 = node2.find('failure')
                    if failure2 is not None:
                        failure2 = node1.find('error')
                    if failure1.attrib.get(self.failure_message) == \
                            failure2.attrib.get(self.failure_message):
                        return True
                except:
                    return False
        return False

    def update_tree(self, file_path, report_type):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for child in root:
            self.add_title(report_type, child)

        old_time = self.root.attrib.get('time')
        new_time = root.attrib.get('time')
        if (old_time is not None) and (new_time is not None):
            if float(old_time) < float(new_time):
                self.root.attrib['time'] = str(new_time)


    def update_status(self):
        count = {"errors": 0, "failures": 0, "skipped": 0, "tests": 0}
        for child in self.root:
            if child.find('failure') is not None:
                count["failures"] += 1
            elif child.find('error') is not None:
                count["errors"] += 1
            elif child.find('skipped') is not None:
                count["skipped"] += 1
            elif child.attrib.get('status') == 'passed':
                pass

        self.root.attrib["errors"] = str(count["errors"])
        self.root.attrib["failures"] = str(count["failures"])
        self.root.attrib["skipped"] = str(count["skipped"])
        self.root.attrib["tests"] = str(len(self.root))

        self.add_cdata()
