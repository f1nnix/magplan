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


prod_requirements = [
    "boto3",
    "celery[redis]",
    "django-ace",
    "django-admin-list-filter-dropdown",
    "django-dynamic-preferences",
    "django-filter",
    "django-picklefield",
    "django-polymorphic",
    "django-widget-tweaks",
    "django>=3.1",
    "html2text",
    "mistune",
    "psycopg2",
    "pymysql",
    "python-slugify",
    "requests",
    "sshtunnel",
]

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
    version="2.0.27",
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
    install_requires=prod_requirements,
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
