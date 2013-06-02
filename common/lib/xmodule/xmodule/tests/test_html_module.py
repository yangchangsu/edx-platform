import unittest

from mock import Mock

from xmodule.html_module import HtmlModule
from xmodule.modulestore import Location

from . import test_system


class HtmlModuleSubstitutionTestCase(unittest.TestCase):
    location = Location(["i4x", "edX", "toy", "html", "simple_html"])
    descriptor = Mock()

    def test_substitution_works(self):
        sample_xml='%%USER_ID%%'
        module_data = {'data': sample_xml}
        module_system = test_system(test_user=Mock(id=1, is_staff=False))
        module = HtmlModule(module_system, self.location, self.descriptor, module_data)
                                            # the hash of user id 1 with anonymous_student_id 'student' and no course secret set
        self.assertEqual(module.get_html(), '509e87a6c45ee0a3c657bf946dd6dc43d7e5502143be195280f279002e70f7d9')
        module_system = test_system(test_user=Mock(id=1, is_staff=False), course_id='Testing/Testing/1.2.3')
        module = HtmlModule(module_system, self.location, self.descriptor, module_data)
                                            # the hash of user id 1 with anonymous_student_id 'student' and test course secret set
        self.assertEqual(module.get_html(), '1eefef2a8834f1ee805537abf8998698e6b25b5ea003d0a8a6f608e28fec41a2')


    def test_substitution_without_magic_string(self):
        sample_xml = '''
            <html>
                <p>Hi USER_ID!11!</p>
            </html>
        '''
        module_data = {'data': sample_xml}
        module = HtmlModule(test_system(), self.location, self.descriptor, module_data)
        self.assertEqual(module.get_html(), sample_xml)


    def test_substitution_without_anonymous_student_id(self):
        sample_xml = '''
            <html>
                <p>%%Hi USER_ID%%!11!</p>
            </html>
        '''
        module_data = {'data': sample_xml}
        module_system = test_system()
        module_system.anonymous_student_id = None
        module = HtmlModule(module_system, self.location, self.descriptor, module_data)
        self.assertEqual(module.get_html(), sample_xml)

