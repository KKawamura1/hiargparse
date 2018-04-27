"""A setup module.

This module is based on [pypa/sampleproject/setup.py](https://github.com/pypa/sampleproject/blob/master/setup.py).
"""

from setuptools import setup, find_packages
from pathlib import Path
import importlib.util

path_to_file = Path(__file__).resolve()
path_to_here = path_to_file.parent

# readme
path_to_readme = path_to_here / 'README.md'
with path_to_readme.open(encoding='utf-8') as f:
    readme = f.read()
readme_type = 'text/markdown'

# version
path_to_version = path_to_here / 'hiargparse' / '_version.py'
_version_spec = importlib.util.spec_from_file_location('_version', location=str(path_to_version))
_version = importlib.util.module_from_spec(_version_spec)
assert _version_spec.loader is not None
_version_spec.loader.exec_module(_version)
VERSION = _version.__VERSION__  # type: ignore

# classifiers
classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

# requirements
requirements = [
    'typing-extensions>=3.6.2.1',
    'pyyaml',
    'toml',
]
python_requires = '~=3.6'

setup(
    name='hiargparse',
    version=VERSION,
    description='A hierarchical and highly sophisticated variant of argparse.',
    long_description=readme,
    long_description_content_type=readme_type,
    url='https://github.com/KKawamura1/hiargparse',
    author='Keigo Kawamura',
    author_email='kkawamura@logos.t.u-tokyo.ac.jp',
    license='MIT',
    classifiers=classifiers,
    keywords='arguments argparse hierarchy',
    project_urls={
        'Source': 'https://github.com/KKawamura1/hiargparse/'
    },
    packages=find_packages(),
    install_requires=requirements,
    python_requires=python_requires,
)
