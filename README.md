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

## Syncing Across Systems

Stufflog automatically syncs your data across multiple computers when your stufflog directory is a Git repository with remotes configured. This feature makes it easy to keep your logs consistent across all your devices.

### Setting Up Git for Stufflogs

1. **Initialize a Git repository** in your stufflog directory:

```bash
cd $STUFFLOG_DIR  # This is typically ~/.stufflog unless you've customized it
git init
```

2. **Create a .gitignore file** (optional) to exclude any private logs:

```bash
echo "private.yml" > .gitignore
```

3. **Make your initial commit**:

```bash
git add .
git commit -m "feat: initial stufflog data"
```

### Connecting to GitHub

1. **Create a new GitHub repository** at https://github.com/new (you can make it private if you prefer)

2. **Connect your local repository to GitHub**:

```bash
git remote add origin https://github.com/yourusername/stufflog-data.git
git branch -M main
git push -u origin main
```

### Automatic Syncing

Once your stufflog directory is a Git repository with a remote configured:

1. Stufflog will automatically detect changes to your log files
2. Changes will be committed to the local Git repository
3. Stufflog will pull from and push to remote repositories (like GitHub) automatically

This means you don't need to run Git commands manually to keep your data in sync. Simply:

1. Set up Git and GitHub as described above on your first computer
2. On additional computers, clone the repository to your stufflog directory:

```bash
git clone https://github.com/yourusername/stufflog-data.git ~/.stufflog
```

Stufflog will handle the rest, ensuring your logs stay synchronized across all your systems while providing version control and backup benefits.

## File Format

Stufflogs are stored as YAML files in the specified directory, with one file per category (e.g., `books.yml`, `movies.yml`).

## Contributing

Contributions to stufflog are welcome! If you'd like to contribute, please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## More Information

For detailed information about the application design, data format, and functionality, see the [DESIGN.md](DESIGN.md) file.
