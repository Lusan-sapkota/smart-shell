#!/usr/bin/env python3
"""
Setup script for Smart-Shell.
"""

from setuptools import setup, find_packages

setup(
    name="smart-shell",
    version="1.0.0",
    description="An intelligent terminal assistant that converts natural language into executable Bash commands",
    author="Lusan Sapkota",
    author_email="contact@lusansapkota.com.np",
    packages=find_packages(),
    py_modules=["main", "shell_builder", "ai_wrapper", "safety", "config", "utils"],
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "google-generativeai>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "smart-shell=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    license="Apache License 2.0",
    keywords="shell bash terminal ai assistant",
    url="https://github.com/Lusan-sapkota/smart-shell",
    project_urls={
        "Bug Tracker": "https://github.com/Lusan-sapkota/smart-shell/issues",
        "Documentation": "https://github.com/Lusan-sapkota/smart-shell/blob/main/README.md",
        "Source Code": "https://github.com/Lusan-sapkota/smart-shell",
        "Author Website": "https://lusansapkota.com.np",
    },
    long_description="""
    Smart-Shell is an intelligent terminal assistant that converts natural language into executable Bash commands.
    It uses Google's Gemini AI models to interpret user requests and generate appropriate shell commands.
    
    Features:
    - Convert natural language to Bash commands
    - Safety checks for potentially dangerous commands
    - Interactive mode for continuous usage
    - Support for multiple Gemini models
    """,
    long_description_content_type="text/markdown",
) 