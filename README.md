# stufflog

A general journalling CLI application that uses YAML files for portability, editability, and readability. Stufflog helps you track and manage various categories of information such as books, movies, moods, or any other type of "stuff" you want to log.

## Installation

You can install stufflog using pip:

```bash
# Install from the current directory
pip install .

# Or directly from GitHub (if repository is public)
# pip install git+https://github.com/username/stufflog.git
```

## Usage

### Initialize a new stufflog

Create a new category of items to track:

```bash
stufflog books init
```

### Add entries

Add entries to your stufflog with a rating and optional comment:

```bash
# Basic entry with title and rating
stufflog books add "Catcher in the Rye" 4

# Entry with title, rating, and comment
stufflog books add "Dune" 5 "Amazing sci-fi book"
```

### Query entries

Search and filter entries in your stufflogs:

```bash
# Find all entries with rating greater than 4
stufflog books query --greater-than=4

# Find all entries with rating less than 3
stufflog books query --less-than=3

# Find entries created after a certain date
stufflog books query --after="2023-10-01"

# Find entries created before a certain date
stufflog books query --before="2023-12-31"

# Combine multiple filters
stufflog books query --greater-than=3 --after="2023-01-01"
```

### Delete entries

Remove entries from your stufflog:

```bash
stufflog books delete "Catcher in the Rye"
```

## Configuration

### Environment Variables

- `STUFFLOG_DIR`: Specifies the directory where stufflog files are stored. If not set, defaults to `~/.stufflog`.

Example:
```bash
# Set a custom directory for your stufflogs
export STUFFLOG_DIR=~/Documents/my-stufflogs
```

## File Format

Stufflogs are stored as YAML files in the specified directory, with one file per category (e.g., `books.yml`, `movies.yml`).

## More Information

For detailed information about the application design, data format, and functionality, see the [DESIGN.md](DESIGN.md) file.
