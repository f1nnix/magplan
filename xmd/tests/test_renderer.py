"""
Every block element test will be automatically
wrapped inside `<p></p>\n`. Thats why every block
test should include this wrapper tag.
"""
from io import BytesIO
from unittest import TestCase
from unittest.mock import patch

import pytest
from django.core.files import File
from django_dynamic_fixture import G

from main.models import Attachment
from xmd.renderer import XMDRenderer


@pytest.mark.django_db
class TestImage(TestCase):
    def setUp(self):
        file1 = File(
            name='file1.jpg',
            file=BytesIO(b'abcdef')
        )
        attachment1 = G(Attachment, original_filename='user_friendly_filename1.jpg', file=file1)

        self.renderer = XMDRenderer(
            attachments=[attachment1]
        )

        self.expected_html = (
            '<figure>'
            '<img src="dummy.jpg" alt="foo" /><figcaption>foo</figcaption>'
            '</figure>'
        )

    @patch('xmd.renderer.get_attachment_original_filename')
    def test_render_image(self, mock_get_attachment_original_filename):
        mock_get_attachment_original_filename.return_value = 'dummy.jpg'

        html = self.renderer.image('bar', 'foo', 'foo')

        mock_get_attachment_original_filename.assert_called_with(
            'bar', self.renderer.attachments
        )
        assert html == self.expected_html
