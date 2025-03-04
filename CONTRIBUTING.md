# Contributing to stufflog

First off, thank you for considering contributing to stufflog! It's people like you that make stufflog such a great tool.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
  - [Development Environment Setup](#development-environment-setup)
  - [Project Structure](#project-structure)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Styleguides](#styleguides)
  - [Git Commit Messages](#git-commit-messages)
  - [Python Styleguide](#python-styleguide)
  - [Documentation Styleguide](#documentation-styleguide)
- [Testing](#testing)
- [Release Process](#release-process)

## Code of Conduct

This project and everyone participating in it is governed by the stufflog Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [project_email@example.com].

## Getting Started

### Development Environment Setup

1. **Fork the repository**:
   Visit the [stufflog repository](https://github.com/yourusername/stufflog) and click the "Fork" button.

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/stufflog.git
   cd stufflog
   ```

3. **Set up a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   # Or if you're using pipenv
   pipenv install --dev
   ```

5. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Project Structure

```
stufflog/
├── src/
│   └── stufflog/  # Main package code
├── tests/         # Test suite
├── docs/          # Documentation
├── examples/      # Example usage
├── pyproject.toml # Project metadata and dependencies
└── ...
```

## How to Contribute

### Reporting Bugs

This section guides you through submitting a bug report for stufflog. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report**
- Check the documentation for tips on using the application correctly
- Check if the issue has already been reported
- Collect information about the bug (steps to reproduce, error messages, etc.)

**How to Submit A Good Bug Report**
Create an issue on the repository and include:
- A clear, descriptive title
- Steps to reproduce the behavior
- Expected vs actual behavior
- Screenshots or terminal output if applicable
- System information (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions include completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion**
- Check if the enhancement has already been suggested
- Determine which repository the enhancement should be suggested in
- Perform a cursory search to see if the enhancement has already been suggested

**How to Submit A Good Enhancement Suggestion**
Create an issue on the repository and provide:
- A clear, descriptive title
- A detailed description of the suggested enhancement
- Specific examples of how this enhancement would be useful
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful to most stufflog users

### Your First Code Contribution

Unsure where to begin contributing to stufflog? You can start by looking through these `beginner` and `help-wanted` issues:

* [Beginner issues](https://github.com/yourusername/stufflog/labels/beginner) - issues which should only require a few lines of code.
* [Help wanted issues](https://github.com/yourusername/stufflog/labels/help%20wanted) - issues which should be a bit more involved than beginner issues.

### Pull Requests

The process described here has several goals:
- Maintain quality
- Fix problems that are important to users
- Engage the community in working toward the best possible stufflog
- Enable a sustainable system for maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. **Create a branch**:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**:
   Make the necessary code changes, following the style guidelines below.

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request**:
   - Submit a pull request from your fork to the main repository
   - Ensure the PR description clearly describes the problem and solution
   - Include the relevant issue number if applicable
   - Follow the pull request template if provided

7. **Code Review**:
   - The maintainers will review your code
   - Address any requested changes
   - Be responsive to feedback

## Styleguides

### Git Commit Messages

We prefer using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages.

**What are Conventional Commits?**

Conventional Commits is a specification for adding human and machine-readable meaning to commit messages. It provides a simple set of rules for creating commit messages that clearly communicate the purpose of a change.

**Why use Conventional Commits?**

- Automatically generate CHANGELOGs
- Easily determine semantic version bumps (based on types of commits)
- Communicate the nature of changes to teammates and other contributors
- Make it easier for new contributors to understand project changes
- Provide better historical context when exploring the codebase

**Format:**

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Common types include:**

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect the meaning of the code (formatting, etc.)
- `refactor`: Code changes that neither fix a bug nor add a feature
- `test`: Adding or updating tests
- `chore`: Changes to build process or auxiliary tools

**Examples:**

```
feat: add user authentication feature

fix(parser): handle edge case with empty input

docs: update installation instructions in README

style: format code according to new style guide

refactor(core): simplify data processing pipeline

test: add integration tests for API endpoints

chore: update dependencies to latest versions

feat(ui)!: redesign user dashboard with breaking changes
```

While we prefer Conventional Commits, the most important thing is that your commit messages are clear, descriptive, and explain the "why" behind the change when necessary.


### Python Styleguide

All Python code is linted with [pylint](https://pylint.pycqa.org/), [flake8](https://flake8.pycqa.org/), and formatted with [black](https://black.readthedocs.io/).

To lint the entire project with pylint:
```bash
pylint $(git ls-files '*.py')
```

You can also specify individual files or directories:
```bash
pylint src/stufflog/some_file.py
```

For style checking with flake8:
```bash
flake8 .
```

Format your code with black:
```bash
black .
```

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters
- Include docstrings for all public modules, functions, classes, and methods
- Use type hints for function parameters and return values
- Sort imports with [isort](https://pycqa.github.io/isort/)
- Follow pylint recommendations to catch errors, enforce best practices, and maintain code quality
- Use black for consistent code formatting (the pre-commit hook will handle this automatically)
- Use flake8 for additional style checking and to ensure code quality

### Documentation Styleguide

- Use [Markdown](https://daringfireball.net/projects/markdown/) for documentation
- Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings
- Include examples in docstrings where appropriate
- Keep documentation updated when changing code

## Testing

This project uses [pytest](https://docs.pytest.org/) for testing. 

- Write tests for all new features and bug fixes
- Aim for high test coverage (at least 80%)
- Run the test suite before submitting a pull request:
  ```bash
  pytest
  ```

- Include both unit tests and integration tests as appropriate
- Mock external dependencies when necessary

## Release Process

This section is primarily for maintainers.

1. Update the version in pyproject.toml according to [semantic versioning](https://semver.org/)
2. Update the CHANGELOG.md
3. Create a new release on GitHub
4. The CI/CD pipeline will automatically publish to PyPI

---

Thank you for contributing to stufflog! Your time and expertise help make this project better for everyone.
