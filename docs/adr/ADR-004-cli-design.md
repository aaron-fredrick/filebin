# ADR 004: CLI Design

## Status
Accepted

## Context
The CLI needs to be intuitive, clean, and provide useful output. However, adding heavyweight CLI frameworks (`click`, `typer`) or output formatting libraries (`rich`) directly to the SDK's core runtime dependencies bloats the installation for users who only want to use the Python API.

## Decision
We chose the Python standard library `argparse` for the CLI. It is lightweight and requires zero external dependencies.

To support beautiful terminal output without forcing the dependency, `rich` is integrated as an optional extra (`[cli-pretty]`). The output formatter `filebin/cli/_output.py` uses a `try/except ImportError` guard to detect if `rich` is installed. If not, it falls back to standard `print()`.

## Consequences
- The base SDK remains extremely lightweight (`aiohttp` only).
- CLI power users can still get rich terminal output by running `pip install filebin[cli-pretty]`.
