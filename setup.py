import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()

requires = [
    'scrypt',
    'pyramid',
    'pyramid_debugtoolbar',
    'pyramid_beaker',
    'waitress',
    'webhelpers',
    ]

setup(name='foo',
      version='0.0',
      description='foo',
      long_description=README,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='foo',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = foo.web.environment:setup
      """,
      paster_plugins=['pyramid'],
      )
