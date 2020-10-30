"""
Every block element test will be automatically
wrapped inside `<p></p>\n`. Thats why every block

test should include this wrapper tag.
"""
from io import BytesIO
from unittest import TestCase
from unittest.mock import patch, Mock

import pytest
from django.core.files import File
from django_dynamic_fixture import G

from magplan.models import Attachment
from magplan.xmd.renderer import XMDRenderer
from magplan.xmd.mappers import plan_internal_mapper


@pytest.mark.django_db
class TestImage(TestCase):
    MOCK_SRC = 'dummy.jpg'
    MOCK_TITLE = 'title'
    MOCK_ALT_TEXT = 'alt_text'

    def setUp(self):
        file1 = File(name='file1.jpg', file=BytesIO(b'abcdef'))
        attachment1 = G(Attachment, original_filename='user_friendly_filename1.jpg', file=file1)

        self.mock_image_mapper = Mock()

        self.renderer = XMDRenderer(image_mapper=self.mock_image_mapper, attachments=[attachment1])

        self.expected_html = (
            '<figure>'
            '<img conf="dummy.jpg" alt="alt_text" /><figcaption>alt_text</figcaption>'
            '</figure>'
        )

    def test_render_image(self):
        self.mock_image_mapper.return_value = self.MOCK_SRC

        html = self.renderer.image(self.MOCK_SRC, self.MOCK_TITLE, self.MOCK_ALT_TEXT)

        self.mock_image_mapper.assert_called_with(self.MOCK_SRC, self.renderer.attachments)
        assert html == self.expected_html
