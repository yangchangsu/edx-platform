# -*- coding: utf-8 -*-
"""Test for Xmodule functional logic."""

import json
import unittest

from lxml import etree

from xmodule.poll_module import PollDescriptor
from xmodule.conditional_module import ConditionalDescriptor
from xmodule.videoalpha_module import VideoAlphaDescriptor


class LogicTest(unittest.TestCase):
    """Base class for testing xmodule logic."""
    descriptor_class = None
    raw_model_data = {}

    def setUp(self):
        class EmptyClass:
            """Empty object."""
            pass

        self.system = None
        self.location = None
        self.descriptor = EmptyClass()

        self.xmodule_class = self.descriptor_class.module_class
        self.xmodule = self.xmodule_class(
            self.system, self.location,
            self.descriptor, self.raw_model_data
        )

    def ajax_request(self, dispatch, get):
        """Call Xmodule.handle_ajax."""
        return json.loads(self.xmodule.handle_ajax(dispatch, get))


class PollModuleTest(LogicTest):
    """Logic tests for Poll Xmodule."""

    descriptor_class = PollDescriptor
    raw_model_data = {
        'poll_answers': {'Yes': 1, 'Dont_know': 0, 'No': 0},
        'voted': False,
        'poll_answer': ''
    }

    def test_bad_ajax_request(self):
        response = self.ajax_request('bad_answer', {})
        self.assertDictEqual(response, {'error': 'Unknown Command!'})

    def test_good_ajax_request(self):
        response = self.ajax_request('No', {})

        poll_answers = response['poll_answers']
        total = response['total']
        callback = response['callback']

        self.assertDictEqual(poll_answers, {'Yes': 1, 'Dont_know': 0, 'No': 1})
        self.assertEqual(total, 2)
        self.assertDictEqual(callback, {'objectName': 'Conditional'})
        self.assertEqual(self.xmodule.poll_answer, 'No')


class ConditionalModuleTest(LogicTest):
    """Logic tests for Conditional Xmodule."""
    descriptor_class = ConditionalDescriptor

    def test_ajax_request(self):
        # Mock is_condition_satisfied
        self.xmodule.is_condition_satisfied = lambda: True
        setattr(self.xmodule.descriptor, 'get_children', lambda: [])

        response = self.ajax_request('No', {})
        html = response['html']

        self.assertEqual(html, [])


class VideoAlphaModuleTest(LogicTest):
    """Logic tests for VideoAlpha Xmodule."""
    descriptor_class = VideoAlphaDescriptor

    raw_model_data = {
        'data': '<videoalpha />'
    }

    def test_get_timeframe_no_parameters(self):
        xmltree = etree.fromstring('<videoalpha>test</videoalpha>')
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, ('', ''))

    def test_get_timeframe_with_one_parameter(self):
        xmltree = etree.fromstring(
            '<videoalpha start_time="00:04:07">test</videoalpha>'
        )
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, (247, ''))

    def test_get_timeframe_with_two_parameters(self):
        xmltree = etree.fromstring(
            '''<videoalpha
                    start_time="00:04:07"
                    end_time="13:04:39"
                >test</videoalpha>'''
        )
        output = self.xmodule._get_timeframe(xmltree)
        self.assertEqual(output, (247, 47079))
