'''
Author: He,Yifan
Date: 2022-02-16 21:49:57
LastEditors: He,Yifan
LastEditTime: 2022-02-18 21:00:08
'''


import os
from setuptools import setup, find_packages


exec(open("pgsyn/__init__.py").read())


def read(fname):
    """Read a file to a string."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="pgsyn",
    version=__version__,
    description="A convenient tool for the experiments on program synthesis based on PyshGP",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    keywords=["push gp", "genetic programming", "pushgp", "gp", "push"],
    author="Yifan He",
    author_email="he.yifan.xs@alumni.tsukuba.ac.jp",
    license="MIT",
    url="https://github.com/Y1fanHE/pgsyn.git",
    packages=find_packages(
        exclude=('examples', 'examples.*', 'tests', 'tests.*', 'docs', 'docs_source')
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        'Programming Language :: Python :: 3',
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    install_requires=[
        "numpy>=1.12.0",
        "scipy>=0.18.0",
        "pandas>=0.23.4",
        "pyrsistent>=0.16.0",
        "pyyaml>=6.0",
    ],
    tests_require=[
        "pytest"
    ],
)