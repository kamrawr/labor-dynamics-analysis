#!/usr/bin/env python3
"""
Setup script for Labor Dynamics Analysis package.
"""

from setuptools import setup, find_packages
import pathlib

# Read the README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

requirements = read_requirements('requirements.txt')

setup(
    name="labor-dynamics-analysis",
    version="0.1.0",
    author="kamrawr",
    author_email="rawrdog92@yahoo.com",
    description="Analysis of College Enrollment and Labor Employment in U.S.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/kamrawr/labor-dynamics-analysis",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": read_requirements("requirements-dev.txt")[1:],  # Skip -r requirements.txt line
    },
    entry_points={
        "console_scripts": [
            "labor-analysis=src.cli:main",
        ],
    },
    package_data={
        "": ["config/*.yaml", "data/raw/*.csv", "data/external/*.json"],
    },
    include_package_data=True,
    zip_safe=False,
)