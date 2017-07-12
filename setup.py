#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '2.1'

__build__ = ''

setup(name='dockerrotate',
      version=__version__ + __build__,
      description='Docker clenaup tool',
      author='Location Labs',
      author_email='info@locationlabs.com',
      url='http://locationlabs.com',
      packages=find_packages(exclude=['*.tests']),
      setup_requires=[
          'nose>=1.3.7',
      ],
      install_requires=[
          'docker>=2.4.2',
          'python-dateutil>=2.6.1',
      ],
      tests_require=[
          'mock',
          'coverage',
      ],
      test_suite='dockerrotate.tests',
      entry_points={
          'console_scripts': [
              'docker-rotate = dockerrotate.main:main',
          ]
      },
      )
