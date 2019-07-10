"""
Django settings for magplan project.

Generated by 'django-admin startproject' using Django 2.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
from collections import OrderedDict
# from django.utils.translation import gettext

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production.sample
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production.sample secret!
SECRET_KEY = os.getenv('SECRET_KEY', '-6w*l1-u(9gy8gnp%e#1nf8-!*8j)e@%l%^ct)77r^6(cixj2v')

# SECURITY WARNING: don't run with debug turned on in production.sample!
DEBUG = True if os.getenv('APP_ENV', None) in ('DEVELOPMENT', 'TEST',) else False

ALLOWED_HOSTS = [] if DEBUG is True else [os.getenv('APP_HOST', None)]
# Application definition

INSTALLED_APPS = [
    'constance',
    'constance.backends.database',
    'django.contrib.admin',
    'django.contrib.auth',
    'polymorphic',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_admin_listfilter_dropdown',
    'main',
    'plan',
    'finance',
    'authtools',
    'debug_toolbar',
    'django_filters',

]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

]

ROOT_URLCONF = 'magplan.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'plan.context_processors.inject_last_issues',  # TODO: use context processor only for plan app
                'plan.context_processors.inject_app_url',  # TODO: use context processor only for plan app

            ],
        },
    },
]

WSGI_APPLICATION = 'magplan.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', 5432),
        'NAME': os.environ.get('DB_NAME', 'postgres'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'en-us')
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]
TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = False 

USE_TZ = True

DATETIME_FORMAT = 'M d, y H:m'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

AUTH_USER_MODEL = 'main.User'

INTERNAL_IPS = ['127.0.0.1']

LOGIN_REDIRECT_URL = '/'

CONSTANCE_CONFIG = {
    'PLAN_EMAIL_USE_TLS': (True, '', bool),
    'PLAN_EMAIL_HOST': ('smtp.gmail.com', '', str),
    'PLAN_EMAIL_USER': ('', '', str),
    'PLAN_EMAIL_PASSWORD': ('', '', str),
    'PLAN_EMAIL_PORT': (587, '', int),
    'PLAN_EMAIL_FROM': ('', '', str),
    'PLAN_EMAIL_SUBJECT_PREFIX': ('[magplan]', '', str),
    'PLAN_POSTS_INSTANCE_CHUNK': ('', 'Instance-specific arbitrary template code', str),

    'FINANCE_EMAIL_USE_TLS': (True, '', bool),
    'FINANCE_EMAIL_HOST': ('smtp.gmail.com', '', str),
    'FINANCE_EMAIL_USER': ('', '', str),
    'FINANCE_EMAIL_PASSWORD': ('', '', str),
    'FINANCE_EMAIL_PORT': (587, '', int),
    'FINANCE_EMAIL_FROM': ('', '', str),
    'FINANCE_EMAIL_SUBJECT_PREFIX': ('[notify]', '', str),

    'SYSTEM_USER_ID': (1, '', int),
}

CONSTANCE_CONFIG_FIELDSETS = OrderedDict({
    'General settings': ('SYSTEM_USER_ID','PLAN_POSTS_INSTANCE_CHUNK',),
    'Plan email settings': ('PLAN_EMAIL_HOST', 'PLAN_EMAIL_PORT', 'PLAN_EMAIL_USE_TLS',
                            'PLAN_EMAIL_USER', 'PLAN_EMAIL_PASSWORD',
                            'PLAN_EMAIL_FROM', 'PLAN_EMAIL_SUBJECT_PREFIX'),
    'Finance email settings': ('FINANCE_EMAIL_HOST', 'FINANCE_EMAIL_PORT', 'FINANCE_EMAIL_USE_TLS',
                               'FINANCE_EMAIL_USER', 'FINANCE_EMAIL_PASSWORD',
                               'FINANCE_EMAIL_FROM', 'FINANCE_EMAIL_SUBJECT_PREFIX'),
})
CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

if DEBUG is False:
    EMAIL_BACKEND = 'main.email.DefaultEmailBackend'

else:
    EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
