import re
import typing as tp
from contextlib import contextmanager

import pymysql
from django.conf import settings
from sshtunnel import SSHTunnelForwarder

from xmd.mappers import s3_public_mapper


@contextmanager
def Lock(post):
    post.is_locked = True
    post.save()
    yield
    post.is_locked = False
    post.save()


def replace_images_paths(xmd: str, attachments: tp.List, mapper: tp.Callable = None) -> str:
    """Replaces all links to local images
    to absolute paths with mapper function.

    Can parse both regualar images and galleries.
    If provided link not found, it's left intact.

    Examples:

        ![](image1.jpg)
        ![](image1.jpg,image2.jpg)
    """
    if not mapper:
        mapper = s3_public_mapper

    img_pattern = re.compile(
        '^'  # Only from beginning
        ' *'  # Some leading spaces may persis 
        '!\[.*?\]\((.+)\)'  # MD image pattern
        ' *?'  # Some ending spaces may persis
        '$'  # Capture urls only from last section
    )

    url_replace_pattern = re.compile(
        '\]\((.+)\)$'  # FIXME: match real last () group
    )

    result_lines = []

    for line in xmd.splitlines():
        # Extract image
        url_chunk = re.findall(img_pattern, line)
        if not url_chunk:  # If no image in line
            result_lines.append(line)
            continue

        # Parse all images for galleries one
        filenames = [
            filename.strip()
            for filename in url_chunk[0].split(',')  # First and only match group
        ]
        absolute_url_chunks = [
            mapper(filename, attachments)
            for filename in filenames
        ]

        # Build result line with new images
        absolute_urs = ']({})'.format(','.join(absolute_url_chunks))
        res_line = re.sub(url_replace_pattern, absolute_urs, line)

        result_lines.append(res_line)

    return '\n'.join(result_lines)


def update_ext_db_xmd(post_id: int, xmd: str):
    """

    :param post_id:
    :param xmd:
    :return:
    """
    if not all(settings.EXT_DB.get(key) for key in settings.EXT_DB.keys()):
        return

    conf = settings.EXT_DB
    with SSHTunnelForwarder(
            (conf['SSH_HOST'], int(conf['SSH_PORT'])),
            ssh_username=conf['SSH_USER'],
            ssh_password=conf['SSH_PASS'],
            remote_bind_address=(conf['EXT_DB_HOST'], int(conf['EXT_DB_PORT']))) as tunnel:
        conn = pymysql.connect(host=conf['EXT_DB_HOST'], user=conf['EXT_DB_USER'],
                               passwd=conf['EXT_DB_PASS'], db=conf['EXT_DB_NAME'],
                               port=tunnel.local_bind_port)
        with conn.cursor() as cursor:
            # TODO: rewrite with update or insert
            retrieve_query = 'SELECT meta_value FROM wp_postmeta WHERE post_id=%s and meta_key="md" limit 1;'
            cursor.execute(retrieve_query, (post_id,))

            # Update existing if found
            existing_rows = cursor.fetchone()
            if existing_rows:
                update_query = 'UPDATE wp_postmeta SET meta_value=%s WHERE post_id=%s and meta_key="md";'
            else:
                update_query = 'INSERT INTO wp_postmeta (meta_value, meta_key, post_id) VALUES (%s, "md", %s);'
            cursor.execute(update_query, (xmd, post_id))
            conn.commit()

        conn.close()
