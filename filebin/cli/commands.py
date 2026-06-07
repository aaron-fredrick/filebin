"""CLI command implementations."""

import argparse
from pathlib import Path

from filebin.cli import _output as output
from filebin.client.async_client import AsyncFilebinClient


async def cmd_upload(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    bin_id = args.bin
    path = Path(args.file)
    if not path.is_file():
        output.print_error(f"File not found: {path}")
        return

    # If no bin provided, Filebin.net assigns one dynamically, but our strict typed
    # client expects an ID. We let the HTTP layer POST to / if bin_id is missing,
    # then redirect catches the new bin ID.
    # For now, require it or generate a local random one for simplicity.
    if not bin_id:
        import uuid

        bin_id = uuid.uuid4().hex[:16]

    file_model = await client.upload_file(bin_id, path)
    output.print_success(f"Uploaded {file_model.filename} to bin {bin_id}")
    output.print_file(file_model)


async def cmd_download(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    dest = await client.download_file(args.bin, args.file, args.output)
    output.print_success(f"Downloaded to {dest}")


async def cmd_list(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    bin_model = await client.list_bin(args.bin)
    output.print_bin(bin_model)


async def cmd_delete_bin(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    await client.delete_bin(args.bin)
    output.print_success(f"Deleted bin {args.bin}")


async def cmd_delete_file(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    await client.delete_file(args.bin, args.file)
    output.print_success(f"Deleted file {args.file} from bin {args.bin}")


async def cmd_archive(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    dest = await client.download_archive(args.bin, args.format, args.output)
    output.print_success(f"Downloaded archive to {dest}")


async def cmd_lock(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    bin_model = await client.lock_bin(args.bin)
    output.print_success(f"Locked bin {bin_model.id}")
    output.print_bin(bin_model)
