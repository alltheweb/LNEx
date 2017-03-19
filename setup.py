"""
Copyright 2017 Hussein S. Al-Olimat, hussein@knoesis.org

This software is released under the GNU Affero General Public License (AGPL)
v3.0 License.
"""


#!/usr/bin/env python
"""
LNEx
"""

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='LNEx',
    version='1',
    description='Location Name Extractor tool (LNEx): extracts location names from targeted text streams',
    long_description=readme,
    author='Hussein S. Al-Olimat',
    author_email='hussein@knoesis.org',
    url='https://github.com/halolimat/LNEx',
    license=license,
    packages=find_packages(exclude=('_Data')),
    package_data={'LNEx': ['_Dictionaries/*.txt']},
    install_requires=[
          'elasticsearch',
          'elasticsearch-dsl',
          'nltk',
          'geopy',
          'texttable',
          'wordsegment'
      ]
)
