#!/usr/bin/env python3
"""
example usage: poetry run python aegis_decrypt.py -h
"""

import argparse
import getpass
import sys
from os import path
from glob import glob
from src.aegis_db import AegisDB
from src.output import Output


def main():
    """
    Aegis decryptor main function.
    """
    parser = argparse.ArgumentParser(
        prog="aegis_decrypt.py",
        description="Decrypt an Aegis vault and produce an output as requested. Exported files are created in the folder `./export/` inside the project itself.",
        add_help=True,
    )
    parser.add_argument(
        "--vault",
        dest="vault",
        required=True,
        help="The encrypted Aegis vault file or a folder containing only Aegis vault files. If it is a folder, the most recent file is considered.",
    )
    # optional args
    parser.add_argument(
        "--entryname",
        dest="entryname",
        required=False,
        help="The name of the entry for which you want to generate the OTP code.",
    )
    parser.add_argument(
        "--issuer",
        dest="issuer",
        required=False,
        help="The name of the issuer for which you want to generate the OTP code.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        required=False,
        choices=["csv", "qrcode", "json", "otp", "stdout"],
        default="otp",
        help="The output format. Default: %(default)s",
    )
    parser.add_argument(
        "--password", dest="password", required=False, help="The encryption password."
    )
    args = parser.parse_args()

    if path.isfile(args.vault):
        db = AegisDB(args.vault, get_password(args))
    elif path.isdir(args.vault):
        files = glob(path.join(args.vault, "*"))  # Get all files in the folder
        if not files:
            raise ValueError(f"Directory {args.vault} is empty.")

        # Sort files by modification time (newest first)
        sorted_files = sorted(files, key=path.getmtime, reverse=True)
        print(f"Using file {sorted_files[0]}")
        db = AegisDB(sorted_files[0], get_password(args))
    else:
        raise ValueError(f"Invalid file or folder: {args.vault}")

    if args.entryname is None and args.issuer is None:
        entries = db.get_all()
    else:
        entries = db.get_by_name(args.entryname, args.issuer)

    if entries:
        output = Output(entries, args.entryname)

        match args.output:
            case "csv":
                output.csv()
            case "qrcode":
                output.qrcode()
            case "json":
                output.json()
            case "otp":
                output.otp()
            case "stdout":
                output.stdout()

    else:
        print("No entries found.")


def get_password(args):
    if args.password is None:
        password = getpass.getpass().encode("utf-8")
    else:
        password = args.password.encode("utf-8")
    return password


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
