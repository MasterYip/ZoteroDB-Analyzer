#!/usr/bin/env python3
"""Setup script for zoterodb_analyzer package."""

from setuptools import setup, find_packages
import os

# Read the README file
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="zoterodb_analyzer",
    version="0.1.0",
    author="ZoteroDB Analyzer Team",
    author_email="contact@zoterodb-analyzer.com",
    description="Zotero Database Analyzer for Literature Review Fast Composing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ZoteroDB-Analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Text Processing :: Markup",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyzotero>=1.5.0",
        "requests>=2.25.0",
        "markdown>=3.3.0",
        "click>=8.0.0",
        "python-dotenv>=0.19.0",
        "jsonschema>=4.0.0",
        "rich>=12.0.0",
        "pathlib>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.910",
        ],
        "mcp": [
            "mcp>=0.1.0",
            "fastapi>=0.68.0",
            "uvicorn>=0.15.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "zoterodb-analyzer=zoterodb_analyzer.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
