#pylint: disable=missing-module-docstring
from setuptools import setup, find_packages

setup(
    name="stufflog",
    version="0.1.0",
    description="A simple command-line tool to log and track things in categories",
    author="Stufflog Team",
    author_email="example@example.com",
    url="https://github.com/yourusername/stufflog",
    packages=find_packages(),
    py_modules=["stufflog"],
    install_requires=[
        "pyyaml",
    ],
    entry_points={
        "console_scripts": [
            "stufflog=stufflog:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)
