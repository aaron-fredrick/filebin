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

    # Generate or validate bin ID using the client's create_bin method
    try:
        bin_model = client.create_bin(bin_id)
        bin_id = bin_model.id
    except ValueError as e:
        output.print_error(str(e))
        return

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


async def cmd_create_bin(args: argparse.Namespace, client: AsyncFilebinClient) -> None:
    try:
        bin_model = client.create_bin(args.bin)
        output.print_success(f"Created/Validated bin ID: {bin_model.id}")
    except ValueError as e:
        output.print_error(str(e))
