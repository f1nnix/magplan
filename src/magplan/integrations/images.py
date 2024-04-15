import os
from contextlib import contextmanager

import boto3


@contextmanager
def S3Client():
    S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")
    S3_ENDPOINT = os.environ.get("S3_ENDPOINT")

    is_requred_params_exist = all(
        (S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME, S3_ENDPOINT)
    )
    if not is_requred_params_exist:
        raise ValueError("Either S3_ACCESS_KEY or S3_SECRET_KEY not provided")

    client = boto3.resource(
        "s3",
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        endpoint_url=S3_ENDPOINT,
    )
    yield (client, S3_BUCKET_NAME)
