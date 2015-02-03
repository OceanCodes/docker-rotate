#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '1.0'

__build__ = ''

setup(name='docker-rotate',
      version=__version__ + __build__,
      description='Docker image rotation tool',
      author='Location Labs',
      author_email='info@locationlabs.com',
      url='http://locationlabs.com',
      packages=find_packages(exclude=['*.tests']),
      setup_requires=[
          'nose>=1.0',
      ],
      install_requires=[
          'docker-py>=0.5.3',
          'python-dateutil>=2.4.0',
      ],
      tests_require=[
          'mock',
      ],
      test_suite='dockerrotate.tests',
      entry_points={
          'console_scripts': [
              'docker-rotate = dockerrotate.main:main',
          ]
      },
      )
