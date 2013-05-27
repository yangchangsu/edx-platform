# -*- coding: utf-8 -*-
"""
Tests of the word cloud in mongo
"""
import json
from operator import itemgetter

from django.test import TestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from student.tests.factories import UserFactory, CourseEnrollmentFactory, UserProfileFactory, AdminFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from mock import patch, DEFAULT
from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from capa.tests.response_xml_factory import StringResponseXMLFactory
from courseware.tests.factories import StudentModuleFactory
from xmodule.modulestore import Location
from xmodule.modulestore.django import modulestore
from lxml import etree
from django.test.client import Client

USER_COUNT = 2

@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class TestWordCloud(ModuleStoreTestCase):

    def get_url(self, dispatch):
        """ Return word cloud url with dispatch """
        return reverse(
            'modx_dispatch',
            args=(self.course.id, self.item_url, dispatch)
        )

    def setUp(self):

        course_data = {}

        self.course = CourseFactory.create(data=course_data)

        modulestore().request_cache = modulestore().metadata_inheritance_cache_subsystem = None

        chapter = ItemFactory.create(
            parent_location=self.course.location,
            template="i4x://edx/templates/sequential/Empty",
        )
        section = ItemFactory.create(
            parent_location=chapter.location,
            template="i4x://edx/templates/sequential/Empty",
            metadata={'graded': True, 'format': 'Homework'}
        )

        self.users = [
            UserFactory.create(username='robot%d' % i, email='robot+test+%d@edx.org' % i)
            for i in xrange(USER_COUNT)
        ]

        for user in self.users:
            CourseEnrollmentFactory.create(user=user, course_id=self.course.id)

        # got from word cloud yaml
        template_name = "i4x://edx/templates/word_cloud/Word_cloud"

        item = ItemFactory.create(
            parent_location=section.location,
            template=template_name,
            data={}
        )
        self.item_url = Location(item.location).url()

        # login all users for acces to word cloud
        self.clients = {user: Client() for user in self.users}
        login_statuses = [self.clients[user].login(username=user.username, password='test')
                          for user in self.users]
        self.assertTrue(all(login_statuses))

        # check word cloud response for every user
        self.responses = {user: self.clients[user].post(self.get_url('get_state')) for user in self.users}

        # word cloud answers to students requests
        self.response_contents = {user: json.loads(response.content) for user, response in
                                  self.responses.items()}
        self.assertEqual(''.join(set([content['status']
                        for user, content in self.response_contents.items()])), 'success')
        # *** SyntaxError: unexpected EOF while parsing (<stdin>, line 1)
        # ipdb> self.client.post(reverse('modx_dispatch',args=(self.course.id, Location(item.location).url(), 'submit')), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # <django.http.HttpResponse object at 0x1081b1f50>
        # ipdb> bbb=self.client.post(reverse('modx_dispatch',args=(self.course.id, Location(item.location).url(), 'submit')), {}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        # ipdb> bbb.content
        # '{"status": "fail", "error": "You have already posted your data."}'

    def test_per_user(self):
        """Test word cloud data flow per single user actions.

            Make sures that:

            1. Inital state of word cloud is correct. Those state that is sended
            from server to frontend, when student loads word cloud page.

            2. Student can submit data succesfully.

            3. Word cloud data properly updates after student's submit.

            4. Next submits produce "already voted" error

            5. State of word cloud is still as in #3.

        """

        # 1)
        # correct initial data:
        correct_initial_data = {u'status': u'success',
                                u'student_words': {},
                                u'total_count': 0,
                                u'submitted': False,
                                u'top_words': {},
                                u'display_student_percents': False}

        for user, content in self.response_contents.items():
            self.assertEquals(content, correct_initial_data)

        # 2)
        input_words = ["small",
                       "BIG",
                       " Spaced ",
                       " few words",
                       u"this is unicode Юникод"]

        correct_words = [u"small",
                         u"big",
                         u"spaced",
                         u"few words",
                         u"this is unicode юникод"]

        self.response_contents = {}
        correct_jsons = {}
        for index, user in enumerate(self.users):
            response = self.clients[user].post(self.get_url('submit'),
                                    {'student_words[]': input_words},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            self.response_contents[user] = json.loads(response.content)

            correct_jsons[user] = {
            u'status': u'success',
            u'submitted': True,
            u'display_student_percents': True,
            u'student_words': {word: 1+index for word in correct_words},
            u'total_count': len(input_words) * (1 + index),
            u'top_words': [{u'text': word, u'percent': 100 / len(input_words), u'size': (1+index)}
                          for word in correct_words]
            }


        for user, content in self.response_contents.items():

            self.maxDiff = None

            # we should compare top_words for manually, because they are unsorted
            keys_to_compare = set(content.keys()).difference(set(['top_words']))
            self.assertDictEqual(
                {k: content[k]      for k in keys_to_compare},
                {k: correct_jsons[user][k] for k in keys_to_compare})

            # comparing top_words:
            top_words_content = sorted(content['top_words'], key=itemgetter('text'))
            top_words_correct = sorted(correct_jsons[user]['top_words'], key=itemgetter('text'))
            self.assertListEqual(top_words_content, top_words_correct)

    # def test_collective_submits(self):
    #     self.assertEquals(self.response.status_code, 200)

