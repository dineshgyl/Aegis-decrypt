#!/usr/bin/env python3
import io
import json

from src.aegis_db import AegisDB
import sys


def main():

    with io.open("./testdata/aegis_plain.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    entries = data["db"]["entries"]

    db = AegisDB("testdata/aegis_encrypted_TEST.json", "test")
    db.encrypt(entries)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
