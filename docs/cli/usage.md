# CLI Usage

The Filebin SDK provides a command-line interface under the `fbin` command.

## Installation

To get rich tables and colored output, install the `cli-pretty` extra:
```bash
pip install filebin[cli-pretty]
```

## Global Flags

* `--json`: Forces all output to raw JSON instead of human-readable text. Useful for piping.
* `--help`: Show command usage.

## Commands

### Upload a file
```bash
# Upload a file. A random bin ID will be generated.
fbin upload my_document.pdf

# Upload a file to a specific bin
fbin upload my_document.pdf --bin my-secret-bin-123
```

### Download a file
```bash
# Download a file to the current directory
fbin download my-secret-bin-123 my_document.pdf

# Download a file to a specific directory
fbin download my-secret-bin-123 my_document.pdf --output /tmp/
```

### List contents
```bash
fbin list my-secret-bin-123
```

### Delete
```bash
# Delete a specific file
fbin delete file my-secret-bin-123 my_document.pdf

# Delete an entire bin
fbin delete bin my-secret-bin-123
```

### Download Archive
```bash
# Download all files in the bin as a single tar archive
fbin archive my-secret-bin-123 tar

# Download as a zip archive to a specific directory
fbin archive my-secret-bin-123 zip --output /tmp/
```

### Lock Bin
```bash
# Mark a bin as read-only. No further files can be uploaded.
fbin lock my-secret-bin-123
```
