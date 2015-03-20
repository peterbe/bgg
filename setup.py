import codecs
import os
import re

# Prevent spurious errors during `python setup.py test`, a la
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html:
try:
    import multiprocessing
except ImportError:
    pass

from setuptools import setup, find_packages


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def find_install_requires():
    return [x.strip() for x in
            read('requirements.txt').splitlines()
            if x.strip() and not x.startswith('#')]


setup(
    name='bgg',
    scripts=['G'],
    version=find_version('bgg/__init__.py'),
    description="A love story with Bugzilla, git and Github",
    long_description=read('README.md') + '\n\n',
    author='Peter Bengtsson',
    author_email='mail@peterbe.com',
    url='https://github.com/peterbe/bgg',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=find_install_requires(),
)
