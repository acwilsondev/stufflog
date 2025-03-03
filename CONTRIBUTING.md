# Contributing to Stufflog

Thank you for your interest in contributing to Stufflog! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [Development Setup](#development-setup)
- [Running Tests](#running-tests)
- [Coding Standards](#coding-standards)
- [Contribution Workflow](#contribution-workflow)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

Please be respectful and considerate of others when contributing to the project. Ensure all interactions are professional and welcoming to everyone.

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```
   git clone https://github.com/YOUR-USERNAME/stufflog.git
   cd stufflog
   ```
3. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Install the package in development mode:
   ```
   pip install -e .
   ```

## Running Tests

We use pytest for testing. The test suite includes unit tests and integration tests for both core functionality and CLI interface.

### Prerequisites

Ensure you have all test dependencies installed:
```
pip install -r requirements.txt
```

### Running the entire test suite

```
pytest
```

### Running with coverage report

```
pytest --cov=stufflog
```

### Running specific tests

To run a specific test file:
```
pytest tests/test_stufflog.py
```

To run a specific test class:
```
pytest tests/test_stufflog.py::TestStufflogInit
```

To run a specific test:
```
pytest tests/test_stufflog.py::TestStufflogInit::test_init_stufflog
```

### Test Structure

- `tests/conftest.py`: Contains test fixtures and setup
- `tests/test_stufflog.py`: Unit tests for core functionality
- `tests/test_cli.py`: Integration tests for the command-line interface

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guide
- Use 4 spaces for indentation (no tabs)
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules

### Code Organization

- Keep functions small and focused on a single task
- Organize related functionality into modules
- Write clear and concise comments

### Git Commit Messages

- Use present tense ("Add feature" not "Added feature")
- First line should be a summary (max 72 characters)
- Reference issues and pull requests where appropriate

## Contribution Workflow

1. Create a new branch for your feature or bugfix:
   ```
   git checkout -b feature/your-feature-name
   ```
   or
   ```
   git checkout -b fix/issue-you-are-fixing
   ```

2. Make your changes and add tests for new functionality

3. Ensure all tests pass:
   ```
   pytest
   ```

4. Commit your changes with a clear commit message

5. Push your branch to your fork:
   ```
   git push origin feature/your-feature-name
   ```

6. Submit a pull request to the main repository
   - Provide a clear description of the changes
   - Reference any related issues

7. Address any feedback from code reviews

## Documentation

- Update documentation for any changes to functionality
- Include docstrings for all new functions and classes
- Ensure README.md remains up-to-date with changes
- Document any new command-line options or features

## Issue Reporting

When reporting issues, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Any relevant logs or screenshots
- Your environment information (OS, Python version, etc.)

Thank you for contributing to Stufflog!

