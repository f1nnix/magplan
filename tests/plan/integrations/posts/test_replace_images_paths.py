from unittest.mock import patch

from plan.integrations.posts import replace_images_paths

MOCK_MAP = 'foo.jpg'


@patch('plan.integrations.posts.s3_public_mapper')
def test_basic(mock_s3_public_mapper):
    mock_s3_public_mapper.return_value = MOCK_MAP
    xmd = (
        '![Title](1.jpg)'
    )

    images = []
    output = replace_images_paths(xmd=xmd, attachments=images)
    assert output == '![Title]({})'.format(MOCK_MAP)


@patch('plan.integrations.posts.s3_public_mapper')
def test_spaces(mock_s3_public_mapper):
    mock_s3_public_mapper.return_value = MOCK_MAP
    xmd = (
        '![Title](    1.jpg    )'
    )

    images = []
    output = replace_images_paths(xmd=xmd, attachments=images)
    assert output == '![Title]({})'.format(MOCK_MAP)


@patch('plan.integrations.posts.s3_public_mapper')
def test_gallery(mock_s3_public_mapper):
    mock_s3_public_mapper.return_value = MOCK_MAP
    xmd = (
        '![Title](1.jpg,2.jpg)'
    )

    images = []
    output = replace_images_paths(xmd=xmd, attachments=images)
    assert output == '![Title]({0},{0})'.format(MOCK_MAP)


@patch('plan.integrations.posts.s3_public_mapper')
def test_gallery_spaces(mock_s3_public_mapper):
    mock_s3_public_mapper.return_value = MOCK_MAP
    xmd = (
        '![Title](    1.jpg ,   2.jpg   )'
    )

    images = []
    output = replace_images_paths(xmd=xmd, attachments=images)
    assert output == '![Title]({0},{0})'.format(MOCK_MAP)


@patch('plan.integrations.posts.s3_public_mapper')
def test_braces_in_title(mock_s3_public_mapper):
    mock_s3_public_mapper.return_value = MOCK_MAP
    xmd = (
        '![Title()](1.jpg)'
    )

    images = []
    output = replace_images_paths(xmd=xmd, attachments=images)
    assert output == '![Title()]({0})'.format(MOCK_MAP)
