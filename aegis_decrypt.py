#!/usr/bin/env python3
"""
example usage: poetry run python aegis_decrypt.py -h
"""

import argparse
import getpass
import sys
import keyring
from os import path, getcwd
import os
from glob import glob
from importlib.metadata import version

from src.aegis_db import AegisDB
from src.output import Output
from datetime import datetime

def main() -> None:
    """
    Aegis decryptor main function.
    """
    AEGIS_DECRYPT_BUILD_TIMESTAMP = datetime.fromtimestamp(path.getmtime(sys.executable)).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    print(f"Build timestamp: {AEGIS_DECRYPT_BUILD_TIMESTAMP}")
    parser = argparse.ArgumentParser(
        prog="aegis_decrypt.py",
        description="Aegis Decrypt v"
        + version("aegis_decrypt")
        + ". This program comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under certain conditions; type 'aegis_decrypt.py --license' for details. "
        "This program decrypts an Aegis vault and produce an output as requested. Exported and unencrypted files are placed in a folder `export/` created inside the folder where the vault is.",
        add_help=True,
    )
    parser.add_argument("--license", help="Show license file.", action="store_true")
    parser.add_argument(
        "--vault",
        dest="vault",
        required=False,
        help="The encrypted Aegis vault file or a folder containing only Aegis vault files. If it is a folder, the most recent file is considered.",
    )
    password_group = parser.add_mutually_exclusive_group()

    password_group.add_argument(
        "--password",
        dest="password",
        required=False,
        help="The vault password. Use it at your own risk since terminal history is usually saved on the device.",
    )

    password_group.add_argument(
        "--password-file",
        dest="password_file",
        required=False,
        help="Read the vault password from the specified file.",
    )

    parser.add_argument(
        "--entryname",
        dest="entryname",
        required=False,
        help="The name of the entry for which you want to generate the output.",
    )
    parser.add_argument(
        "--issuer",
        dest="issuer",
        required=False,
        help="The name of the issuer for which you want to generate the output.",
    )
    parser.add_argument(
        "--search",
        dest="search",
        required=False,
        help="Search for a string in all fields of all entries including the note field.",
    )
    parser.add_argument(
        "--output",
        dest="output",
        required=False,
        choices=["csv", "csv_otpauth", "json", "otp", "qrcode", "stdout"],
        default="otp",
        help="The output format. OTP generation is supported only for TOTP protocol. `qrcode` is the most suitable format for printing a paper backup. Default: %(default)s",
    )

    args = parser.parse_args()

    if args.license:
        with open("LICENSE", "r") as file:
            content = file.read()
        print(content)
        sys.exit()

    if args.vault is None:
        args.vault = getcwd()
        print(f"No vault specified. Using current directory: {args.vault}")

    if path.isfile(args.vault):
        db = AegisDB(args.vault, _get_password(args))
    elif path.isdir(args.vault):
        files = glob(
            path.join(args.vault, "aegis-backup*.json")
        )  # Get only JSON files in the folder
        if not files:
            raise ValueError(
                f"Directory {args.vault} contains no aegis-backup*.json vault files."
            )

        # Sort files by modification time (newest first)
        sorted_files = sorted(files, key=path.getmtime, reverse=True)
        print(f"Using file {sorted_files[0]}")
        db = AegisDB(sorted_files[0], _get_password(args))
    else:
        raise ValueError(f"Invalid file or folder: {args.vault}")

    if args.search is not None:
        entries = db.search(args.search)
        print(f"Found {len(entries)} entries matching search term '{args.search}'.")
    elif args.entryname is None and args.issuer is None:
        entries = db.get_all()
        print(f"Found {len(entries)} entries.")
    else:
        entries = db.get_by_name(args.entryname, args.issuer)
        print(
            f"Found {len(entries)} entries filtering by {args.entryname} entry name and {args.issuer} issuer."
        )

    if entries:
        output = Output(
            entries=entries,
            entry_name=args.entryname,
            export_base_path=path.dirname(db.get_db_path()),
            search_term=args.search,
            source_filename=db.get_db_path()
        )

        match args.output:
            case "csv":
                output.csv()
            case "csv_otpauth":
                output.csv_otpauth()
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


def _get_password(args) -> str:

    # 1. --password
    if args.password is not None:
        return args.password
    
    # 2. --password-file
    if args.password_file is not None:
        try:
            with open(args.password_file, "r") as file:
                password = file.read().rstrip("\r\n")
        except OSError as e:
            raise ValueError(
                f"Unable to read password file '{args.password_file}': {e}"
            ) from e

        if not password:
            raise ValueError(
                f"Password file '{args.password_file}' is empty."
            )

        return password
    
    #3  AEGIS_DECRYPT_PASSWORD environment variable
        ## set in powershell: $env:AEGIS_DECRYPT_PASSWORD = 'xxxxxx'
        ## set in cmd: set "AEGIS_DECRYPT_PASSWORD=xxxxxx"
        ## delete in powershell: $env:AEGIS_DECRYPT_PASSWORD = $null
        ## delete in cmd: set "AEGIS_DECRYPT_PASSWORD="

    password = os.environ.get("AEGIS_DECRYPT_PASSWORD")
    if password is not None:
        print("Password found in environment variable AEGIS_DECRYPT_PASSWORD.")
        return password

    # 4. Windows/Linux Credential Manager
        ## Set the password - python -m keyring set aegis_decrypt vault
        ## Get the password - python -m keyring get aegis_decrypt vault
        ## update the password - python -m keyring set aegis_decrypt vault
        ## Delete the password - python -m keyring del aegis_decrypt vault
    password = keyring.get_password("aegis_decrypt", "vault")
    if password is not None:
        print("Password found in OS Credential Manager.")
        return password
    
    # 5. Interactive prompt
    return getpass.getpass("Vault password: ") 


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
