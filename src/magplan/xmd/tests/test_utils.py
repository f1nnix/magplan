import io
from unittest import TestCase

import pytest
from django.core.files import File
from django_dynamic_fixture import G

from magplan.models import Attachment
from magplan.xmd.utils import get_attachment_original_filename


@pytest.mark.django_db
class Test_get_attachment_original_filename(TestCase):
    def setUp(self):
        file1 = File(
            name='file1.jpg',
            file=io.BytesIO(b'abcdef')
        )
        file2 = File(
            name='file2.jpg',
            file=io.BytesIO(b'abcdef')
        )

        attachment1 = G(Attachment, original_filename='user_friendly_filename1.jpg', file=file1)
        attachment2 = G(Attachment, original_filename='user_friendly_filename2.jpg', file=file2)
        self.attachments = [attachment1, attachment2]

    def test_retrieve_filename(self):
        # filename is returned with full URL path and internal hash
        # So e're checking only filename matches.
        filename = get_attachment_original_filename('user_friendly_filename1.jpg', self.attachments)
        assert 'file1' in filename

    def test_non_existing_filename(self):
        filename = get_attachment_original_filename('404.jpg', self.attachments)
        assert not filename
