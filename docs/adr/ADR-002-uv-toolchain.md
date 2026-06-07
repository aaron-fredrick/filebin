# ADR 002: UV Toolchain Adoption

## Status
Accepted

## Context
The project previously used a mix of `requirements.txt`, `hatchling`, and unmanaged tooling. Dependency management and CI run times were slow and fragmented.

## Decision
We will standardize entirely on `uv`. `pyproject.toml` is the sole source of truth for dependencies.
`uv` will be used for:
- Environment management (`uv sync`)
- Package building (`uv build`)
- Publishing (`uv publish`)
- Tool running (`uv run ruff`, `uv run pytest`)

## Consequences
- Single binary toolchain.
- Blazing fast CI pipelines.
- Elimination of `requirements.txt` and `poetry.lock`.
