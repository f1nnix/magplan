from django.conf import settings as django_settings

SYSTEM_USER_ID = getattr(django_settings, 'SYSTEM_USER_ID', 'foo@bar.baz')
PLAN_EMAIL_FROM = getattr(django_settings, 'PLAN_EMAIL_FROM', 'foo@bar.baz')
EXTERNAL_PARSER_URL = getattr(django_settings, 'EXTERNAL_PARSER_URL', None)
PLAN_POSTS_INSTANCE_CHUNK = getattr(django_settings, 'PLAN_POSTS_INSTANCE_CHUNK', None)
PLAN_EMAIL_SUBJECT_PREFIX = getattr(django_settings, 'PLAN_EMAIL_SUBJECT_PREFIX', '[magplan]')

APP_HOST = getattr(django_settings, 'APP_HOST', 'magpplan.example.com')
APP_URL = getattr(django_settings, 'APP_URL', 'https://magpplan.example.com')
APP_ENV = getattr(django_settings, 'APP_ENV', 'PRODUCTION')

SSH_HOST = getattr(django_settings, 'SSH_HOST', '127.0.0.1')
SSH_PORT = getattr(django_settings, 'SSH_PORT', 22)
SSH_USER = getattr(django_settings, 'SSH_USER', 'user')
SSH_PASS = getattr(django_settings, 'SSH_PASS', 'password')

EXT_DB_HOST = getattr(django_settings, 'EXT_DB_HOST', '127.0.0.1')
EXT_DB_PORT = getattr(django_settings, 'EXT_DB_PORT', '5432')
EXT_DB_NAME = getattr(django_settings, 'EXT_DB_NAME', 'database')
EXT_DB_USER = getattr(django_settings, 'EXT_DB_USER', 'db_user')
EXT_DB_PASS = getattr(django_settings, 'EXT_DB_PASS', 'db_pass')

S3_ACCESS_KEY = getattr(django_settings, 'S3_ACCESS_KEY', 's3_access_key')
S3_SECRET_KEY = getattr(django_settings, 'S3_SECRET_KEY', 's3_secret_key')
S3_BUCKET_NAME = getattr(django_settings, 'S3_BUCKET_NAME', 's3_bucket_name')
