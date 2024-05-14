#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()

setup(
    name="object_symbols_parser",
    version="0.1.2",
    description="Object symbol table wrangler. Useful for finding static memory and code size usage in embedded systems.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/snhobbs/object_symbols_parser",
    author="Simon Hobbs",
    author_email="simon.hobbs@electrooptical.net",
    license="MIT",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas",
        "click",
    ],
    test_suite="nose.collector",
    tests_require=["nose"],
    scripts=["object_symbols_parser.py"],
    include_package_data=True,
    zip_safe=True,
)
