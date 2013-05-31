# -*- coding: utf-8 -*-
"""Test for WordCloud Xmodule functional logic."""

import unittest
from mock import Mock

from xmodule.word_cloud_module import WordCloudModule
from xmodule.modulestore import Location
from xmodule.tests import test_system


class WordCloudFactory(object):
    """A helper class to create Word Cloud modules with various
    parameters for testing.
    """

    # raw word_cloud tag
    data = """
        <word_cloud num_inputs="5" num_top_words="10"
        display_student_percents="False" />
    """

    @staticmethod
    def create():
        """Method return WordCloud Xmodule instance."""
        location = Location(["i4x", "edX", "word_cloud", "default",
                             "SampleProblem{0}".format(1)])
        model_data = {'data': WordCloudFactory.data}

        descriptor = Mock()

        system = test_system()
        system.render_template = lambda template, context: context
        module = WordCloudModule(system, location, descriptor, model_data)

        return module


class WordCloudModuleUnitTest(unittest.TestCase):
    """Unit tests for WordCloud Xmodule."""

    def test_word_cloud_constructor(self):
        """Make sure that all parameters extracted correclty from xml"""
        module = WordCloudFactory.create()

        # `get_html` return only context, cause we
        # overwrite `system.render_template`
        context = module.get_html()

        expected_context = {
            'element_class': 'default',
            'ajax_url': 'courses/course_id/modx/a_location',
            'element_id': 'i4x-edX-word_cloud-default-SampleProblem1',
            'num_inputs': 5,
            'submitted': False
        }
        self.assertDictEqual(context, expected_context)
