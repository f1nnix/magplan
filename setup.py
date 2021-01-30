#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
from glob import glob

from setuptools import find_packages
from setuptools import setup

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def get_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)


test_requirements = [
    "django-functest>=1.0.3,<1.1",
    "pytest>=5.3,<5.4",
    "pytest-django",
    "pytest-cov",
    "pytest-pythonpath",
]

test_lint_requirements = [
    "flake8>=3.7,<3.8",
    # Somewhat pin black, such that older code bases can
    # be verified CI without linting them lots
    "black>=20.8b1,<20.9",
    "pre-commit",
]

setup_requirements = [
    "pytest-runner",
]

development_requirements = test_requirements + test_lint_requirements

extras_requirements = {
    "devel": development_requirements,
    "test": test_requirements,
    "testlint": test_lint_requirements,
    "transifex": ["transifex-client"],
}

setup(
    name="magplan",
    version="2.0.12",
    author="Ilya Rusanen",
    author_email="ilya@rusanen.co.uk",
    url="",
    description="Project management system for publishers, magazines and content creators",
    license="MIT",
    keywords=["django", "crm", "markdown"],
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[
        os.path.splitext(os.path.basename(path))[0] for path in glob("src/*.py")
    ],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    install_requires=[
        "amqp==5.0.2; python_version >= '3.6'",
        "asgiref==3.3.1; python_version >= '3.5'",
        "bcrypt==3.2.0; python_version >= '3.6'",
        "billiard==3.6.3.0",
        "boto3==1.16.43",
        "botocore==1.19.43",
        "celery[redis]==5.0.5",
        "certifi==2020.12.5",
        "cffi==1.14.4",
        "chardet==4.0.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "click==7.1.2; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "click-didyoumean==0.0.3",
        "click-plugins==1.1.1",
        "click-repl==0.1.6",
        "cryptography==3.3.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4, 3.5'",
        "django==3.1.4",
        "django-ace==1.0.10",
        "django-admin-list-filter-dropdown==1.0.3",
        "django-dynamic-preferences==1.10.1",
        "django-widget-tweaks==1.4.8",
        "django-filter==2.4.0",
        "django-picklefield==3.0.1",
        "django-polymorphic==3.0.0",
        "html2text==2020.1.16",
        "idna==2.10; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "jmespath==0.10.0; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "kombu==5.0.2; python_version >= '3.6'",
        "mistune==0.8.4",
        "paramiko==2.7.2",
        "persisting-theory==0.2.1",
        "prompt-toolkit==3.0.8; python_full_version >= '3.6.1'",
        "psycopg2==2.8.6",
        "pycparser==2.20; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "pymysql==0.10.1",
        "pynacl==1.4.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-slugify==4.0.1",
        "pytz==2020.4",
        "redis==3.5.3",
        "requests==2.25.1",
        "s3transfer==0.3.3",
        "six==1.15.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "sqlparse==0.4.1; python_version >= '3.5'",
        "sshtunnel==0.3.1",
        "text-unidecode==1.3",
        "urllib3==1.26.2; python_version != '3.4'",
        "vine==5.0.0; python_version >= '3.6'",
        "wcwidth==0.2.5",
    ],
    dependency_links=[],
    extra_require={},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    include_package_data=True,
    setup_requires=setup_requirements,
    tests_require=test_requirements,
    extras_require={},
)
