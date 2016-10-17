from distutils.core import setup

setup(
    name='RINEXer',
    version='1.0',
    description='Python module for parsing metadata from RINEX data files',
    author='Brandon Owen',
    author_email='brandon.owen@hotmail.com',
    packages=['rinexer'],
    dependency_links=['https://github.com/sighingnow/parsec.py.git#egg=parsec']
)
