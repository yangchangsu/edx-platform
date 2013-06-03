# -*- coding: utf-8 -*-
"""Video xmodule tests in mongo."""

from . import BaseTestXmodule
from .test_videoalpha_xml import SOURCE_XML


class TestVideo(BaseTestXmodule):
    """Integration tests: web client + mongo."""

    TEMPLATE_NAME = "i4x://edx/templates/videoalpha/Video_Alpha"
    DATA = SOURCE_XML
    MODEL_DATA = {
        'data': DATA
    }

    def test_handle_ajax_dispatch(self):
        responses = {
            user.username: self.clients[user.username].post(
                self.get_url('whatever'),
                {},
                HTTP_X_REQUESTED_WITH='XMLHttpRequest')
            for user in self.users
        }

        self.assertEqual(
            set([
                response.status_code
                for _, response in responses.items()
                ]).pop(),
            404)

    def test_videoalpha_constructor(self):
        """Make sure that all parameters extracted correclty from xml"""

        # `get_html` return only context, cause we
        # overwrite `system.render_template`
        context = self.item_module.get_html()
        expected_context = {
            'data_dir': None,
            'caption_asset_path': '/c4x/MITx/999/asset/subs_',
            'show_captions': 'true',
            'display_name': 'Videoalpha 5',
            'end': 3610.0,
            'id': self.item_module.location.html_id(),
            'sources': {
                'main': '.../mit-3091x/M-3091X-FA12-L21-3_100.mp4',
                'mp4': '.../mit-3091x/M-3091X-FA12-L21-3_100.mp4',
                'ogv': '.../mit-3091x/M-3091X-FA12-L21-3_100.ogv',
                'webm': '.../mit-3091x/M-3091X-FA12-L21-3_100.webm'
            },
            'start': 3603.0,
            'sub': None,
            'track': None,
            'youtube_streams': '0.75:jNCf2gIqpeE,1.0:ZwkTiUPN0mg,1.25:rsq9auxASqI,1.50:kMyNdzVHHgg'
        }
        self.assertDictEqual(context, expected_context)
