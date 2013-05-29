# -*- coding: utf-8 -*-
"""Word cloud integration tests using mongo modulestore."""

import json
from operator import itemgetter

from . import BaseTestXmodule


class TestWordCloud(BaseTestXmodule):
    """Integration test for word cloud xmodule."""
    TEMPLATE_NAME = "i4x://edx/templates/word_cloud/Word_cloud"

    def test_single_and_collective_users_submits(self):
        """Test word cloud data flow per single and collective users submits.

            Make sures that:

            1. Inital state of word cloud is correct. Those state that
            is sended from server to frontend, when students load word
            cloud page.

            2. Students can submit data succesfully.

            3. Word cloud data properly updates after students submit.

            4. Next submits produce "already voted" error. Next submits for user
            are not allowed by user interface, but techically it possible, and
            word_cloud should properly react.

            5. State of word cloud after #4 is still as in #3.
        """

        def check_word_cloud_response(response_contents, correct_jsons):
            """Utility function that compares correct and real responses."""
            for username, content in response_contents.items():

                # Used in debugger for comparing objects.
                # self.maxDiff = None

                # We should compare top_words for manually,
                # because they are unsorted.
                keys_to_compare = set(content.keys()).difference(set(['top_words']))
                self.assertDictEqual(
                    {k: content[k] for k in keys_to_compare},
                    {k: correct_jsons[username][k] for k in keys_to_compare})

                # comparing top_words:
                top_words_content = sorted(
                    content['top_words'],
                    key=itemgetter('text')
                )
                top_words_correct = sorted(
                    correct_jsons[username]['top_words'],
                    key=itemgetter('text')
                )
                self.assertListEqual(top_words_content, top_words_correct)

        # check word cloud response for every user
        responses = {
            user.username: self.clients[user.username].post(self.get_url('get_state'))
            for user in self.users
        }

        # word cloud answers to students requests
        response_contents = {
            username: json.loads(response.content) for username, response in
            responses.items()
        }
        self.assertEqual(
            ''.join(set([
                        content['status']
                        for _, content in response_contents.items()
                        ])),
            'success')

        # 1)
        # correct initial data:
        correct_initial_data = {
            u'status': u'success',
            u'student_words': {},
            u'total_count': 0,
            u'submitted': False,
            u'top_words': {},
            u'display_student_percents': False
        }

        for _, response_content in response_contents.items():
            self.assertEquals(response_content, correct_initial_data)

        # 2)
        input_words = [
            "small",
            "BIG",
            " Spaced ",
            " few words",
            u"this is unicode Юникод"
        ]

        correct_words = [
            u"small",
            u"big",
            u"spaced",
            u"few words",
            u"this is unicode юникод"
        ]

        response_contents = {}
        correct_jsons = {}
        for index, user in enumerate(self.users):
            response = self.clients[user.username].post(
                self.get_url('submit'),
                {'student_words[]': input_words},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            response_contents[user.username] = json.loads(response.content)

            correct_jsons[user.username] = {
                u'status': u'success',
                u'submitted': True,
                u'display_student_percents': True,
                u'student_words': {word: 1 + index for word in correct_words},
                u'total_count': len(input_words) * (1 + index),
                u'top_words': [
                    {
                        u'text': word, u'percent': 100 / len(input_words),
                        u'size': (1 + index)
                    }
                    for word in correct_words
                ]
            }

        # 3)
        check_word_cloud_response(response_contents, correct_jsons)

        # 4)
        response_contents = {}
        for index, user in enumerate(self.users):
            response = self.clients[user.username].post(
                self.get_url('submit'),
                {'student_words[]': input_words},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            response_contents[user.username] = json.loads(response.content)

        self.assertEqual(
            ''.join(set([
                        content['status']
                        for _, content in response_contents.items()
                        ])),
            'fail')

        # 5)
        response_contents = {}
        correct_jsons = {}
        for index, user in enumerate(self.users):
            response = self.clients[user.username].post(self.get_url('get_state'))
            response_contents[user.username] = json.loads(response.content)

            correct_jsons[user.username] = {
                u'status': u'success',
                u'submitted': True,
                u'display_student_percents': True,
                u'student_words': {word: self.USER_COUNT for word in correct_words},
                u'total_count': len(input_words) * self.USER_COUNT,
                u'top_words': [
                    {
                        u'text': word, u'percent': 100 / len(input_words),
                        u'size': self.USER_COUNT
                    }
                    for word in correct_words
                ]
            }
        check_word_cloud_response(response_contents, correct_jsons)
