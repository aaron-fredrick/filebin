# CLI Reference

Filebin.py comes with a built-in terminal CLI once installed via pip.

```bash
# If installed via pip
filebin <command> [args]
```

## Commands

### Show Bin Info
Show meta information about a bin, including its size, number of files, and expiration dates.

```bash
filebin bin <bin_id>
```

### Upload a File
Upload a local file to a new or existing bin.

```bash
filebin upload <bin_id> <file>
```

### Download a File
Download a specific file from a bin. You can optionally specify a destination folder.

```bash
filebin download <bin_id> <file> [--path <dir>]
```

### Download Archive
Download an entire bin's contents as a single Zip or Tar file.

```bash
# Download zip
filebin archive <bin_id> zip [--path <dir>]

# Download tar
filebin archive <bin_id> tar [--path <dir>]
```

### Delete a File
Flag a single file for deletion inside a bin.

```bash
filebin delete-file <bin_id> <file>
```

### Delete a Bin
Delete an entire bin and all files inside of it permanently.

```bash
filebin delete-bin <bin_id>
```

### Lock a Bin
Make a bin entirely read-only. It will no longer accept uploads or edits.

```bash
filebin lock <bin_id>
```
