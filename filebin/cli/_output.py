"""CLI output formatting."""

from __future__ import annotations

import dataclasses
import json
import sys
from typing import Any

from filebin.models.bin import BinModel
from filebin.models.file import FileModel

try:
    from rich.console import Console
    from rich.table import Table

    _RICH = True
except ImportError:
    _RICH = False


_JSON_MODE = False


def set_json_mode(enabled: bool) -> None:
    """Toggle JSON output mode globally."""
    global _JSON_MODE
    _JSON_MODE = enabled


def print_success(msg: str) -> None:
    if _JSON_MODE:
        return
    if _RICH:
        Console().print(f"[green]✓ {msg}[/green]")
    else:
        print(f"✓ {msg}")


def print_error(msg: str) -> None:
    if _JSON_MODE:
        print(json.dumps({"error": msg}))
    elif _RICH:
        Console(stderr=True).print(f"[red]Error: {msg}[/red]")
    else:
        print(f"Error: {msg}", file=sys.stderr)


def _to_dict(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj):
        # We drop the 'files' list for bin output to keep JSON flat unless listing
        d = dataclasses.asdict(obj)  # type: ignore[arg-type]
        for k, v in d.items():
            if hasattr(v, "isoformat"):
                d[k] = v.isoformat()
        return d
    return obj


def print_file(file_model: FileModel) -> None:
    if _JSON_MODE:
        print(json.dumps(_to_dict(file_model), indent=2))
        return

    if _RICH:
        console = Console()
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value")
        table.add_row("Filename", file_model.filename)
        table.add_row("Content-Type", str(file_model.content_type))
        table.add_row("Size (bytes)", str(file_model.bytes))
        table.add_row("SHA256", str(file_model.sha256))
        console.print(table)
    else:
        print(f"Filename:     {file_model.filename}")
        print(f"Content-Type: {file_model.content_type}")
        print(f"Size:         {file_model.bytes} bytes")
        print(f"SHA256:       {file_model.sha256}")


def print_bin(bin_model: BinModel) -> None:
    if _JSON_MODE:
        d = _to_dict(bin_model)
        # Ensure we serialize files correctly
        d["files"] = [_to_dict(f) for f in bin_model.files]
        print(json.dumps(d, indent=2))
        return

    if _RICH:
        console = Console()
        console.print(f"\n[bold blue]Bin: {bin_model.id}[/bold blue]")
        console.print(f"Read-only: {bin_model.readonly}")
        console.print(f"Total size: {bin_model.bytes} bytes")

        if bin_model.files:
            console.print(f"\n[bold]Files ({len(bin_model.files)}):[/bold]")
            table = Table()
            table.add_column("Filename", style="cyan")
            table.add_column("Content-Type")
            table.add_column("Size")
            for f in bin_model.files:
                table.add_row(f.filename, str(f.content_type), str(f.bytes))
            console.print(table)
        else:
            console.print("\n[yellow]No files in this bin.[/yellow]")
    else:
        print(f"\nBin: {bin_model.id}")
        print(f"Read-only: {bin_model.readonly}")
        print(f"Total size: {bin_model.bytes} bytes")
        print(f"Files: {len(bin_model.files)}")
        for f in bin_model.files:
            print(f"  - {f.filename} ({f.bytes} bytes, {f.content_type})")
