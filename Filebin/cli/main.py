"""Main CLI entry point."""

import argparse
import asyncio
import sys

from filebin.__version__ import __version__
from filebin.cli import _output as output
from filebin.cli import commands
from filebin.client.async_client import AsyncFilebinClient
from filebin.core.errors import FilebinError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fbin",
        description="Filebin.net CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--json", action="store_true", help="Output raw JSON instead of human-readable text"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # fbin upload <file> [--bin <bin>]
    p_upload = subparsers.add_parser("upload", help="Upload a file to a bin")
    p_upload.add_argument("file", help="Path to local file")
    p_upload.add_argument("--bin", help="Bin ID (generates randomly if omitted)")

    # fbin download <bin> <file> [--output <dir>]
    p_download = subparsers.add_parser("download", help="Download a file from a bin")
    p_download.add_argument("bin", help="Bin ID")
    p_download.add_argument("file", help="Filename")
    p_download.add_argument("--output", default=".", help="Output directory (default: current)")

    # fbin list <bin>
    p_list = subparsers.add_parser("list", help="List files in a bin")
    p_list.add_argument("bin", help="Bin ID")

    # fbin delete
    p_delete = subparsers.add_parser("delete", help="Delete a bin or file")
    d_sub = p_delete.add_subparsers(dest="delete_target", required=True)

    d_bin = d_sub.add_parser("bin", help="Delete entire bin")
    d_bin.add_argument("bin", help="Bin ID")

    d_file = d_sub.add_parser("file", help="Delete single file")
    d_file.add_argument("bin", help="Bin ID")
    d_file.add_argument("file", help="Filename")

    # fbin archive <bin> <zip|tar>
    p_archive = subparsers.add_parser("archive", help="Download entire bin as archive")
    p_archive.add_argument("bin", help="Bin ID")
    p_archive.add_argument("format", choices=["zip", "tar"], help="Archive format")
    p_archive.add_argument("--output", default=".", help="Output directory")

    # fbin lock <bin>
    p_lock = subparsers.add_parser("lock", help="Lock a bin (read-only)")
    p_lock.add_argument("bin", help="Bin ID")

    return parser


async def _main(args: argparse.Namespace) -> None:
    output.set_json_mode(args.json)

    async with AsyncFilebinClient() as client:
        try:
            if args.command == "upload":
                await commands.cmd_upload(args, client)
            elif args.command == "download":
                await commands.cmd_download(args, client)
            elif args.command == "list":
                await commands.cmd_list(args, client)
            elif args.command == "delete":
                if args.delete_target == "bin":
                    await commands.cmd_delete_bin(args, client)
                else:
                    await commands.cmd_delete_file(args, client)
            elif args.command == "archive":
                await commands.cmd_archive(args, client)
            elif args.command == "lock":
                await commands.cmd_lock(args, client)
        except FilebinError as exc:
            output.print_error(str(exc))
            sys.exit(1)


def entry_point() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        asyncio.run(_main(args))
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    entry_point()
