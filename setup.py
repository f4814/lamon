# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='lamon',
    version='0.0.1',
    description='Infomonitor for Lan Paries',
    long_description=readme,
    author='Fabian Geiselhart',
    author_email='me@f4814n.de',
    url='https://github.com/f4814/lamon',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
