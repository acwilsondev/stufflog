# Design

`stufflog` is a general journalling CLI application that uses yaml files for portability, editability, and readability. It can be used for reviewing experiences, a mood journal, etc.

## File Format

This demonstrates the file format for `stufflog`.

```markdown
# Entries

## Dune
- **Datetime**: 2023-10-01T12:00:00Z
- **Title**: Dune
- **Rating**: 5
- **Comment**: Amazing sci-fi book

## Catcher in the Rye
- **Datetime**: 2023-10-02T15:30:00Z
- **Rating**: 3
```

## File Locations

`stufflog` respects `$STUFFLOG_DIR` if it is set, otherwise all files are stored in `~/.stufflog`.

Stuff logs are saved as `[category name].yml`, e.g. `books.yml`, `movies.yml`, `moods.yml`.

A new stufflog cannot be created with the same category as an existing stufflog.

## CLI

Initialize a stufflog:

```bash
stufflog books init
```

This command initializes a new stufflog for the category "books".

Add an entry:

```bash
stufflog books add "Catcher in the Rye" 4
stufflog books add Dune 5 "Amazing sci-fi book"
```

This command adds a new entry to the "books" stufflog with a rating and an optional comment.

Query the stufflog:

```bash
stufflog books query --greater-than=4
# --less-than [int]
# --after [date | datetime]
# --before [date | datetime]
```

This command queries the "books" stufflog for entries with a rating greater than 4. Additional filters can be applied using the --less-than, --after, and --before options.

Delete an entry:
```bash
stufflog books delete "Catcher in the Rye"
```

This command deletes the entry titled "Catcher in the Rye" in the books stufflog.

## Environment Variables

`stufflog` respects the `$STUFFLOG_DIR` environment variable. If it is set, all files are stored in the specified directory. Otherwise, all files are stored in `~/.stufflog`.

## Error Handling

If a new stufflog is created with the same category as an existing stufflog, an error message will be displayed:

```bash
Error: A stufflog with the category "books" already exists.
```

An entry cannot be created with the same name as an existing entry in the same stufflog.

```bash
$ stufflog books add Dune 5
Error: An entry titled "Dune" already exists. Did you mean "stufflog books edit Dune --rating=5"?
```
