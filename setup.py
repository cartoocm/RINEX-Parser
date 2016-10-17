from distutils.core import setup

setup(
    name='RINEXer',
    version='1.0',
    description='Python module for parsing metadata from RINEX data files',
    author='Brandon Owen',
    author_email='brandon.owen@hotmail.com',
    packages=['rinexer'],
    install_requires=['parsec==3.0'],
    dependency_links=['http://github.com/sighingnow/parsec.py/tarball/master#egg=parsec-3.0']
)
