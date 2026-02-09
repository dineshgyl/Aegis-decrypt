import csv
import io
import json
import os

from src.entry_totp import EntryTOTP
from urllib.parse import quote

class Output:
    """
    Class to control the output format.
    """

    _FILENAME_PLAIN = "aegis_plain"

    def __init__(self, entries: list, entry_name:str|None = None, export_base_path: str = "."):
        self._entries = entries
        self._export_path = export_base_path + "/export/"

        os.makedirs(os.path.dirname(self._export_path), exist_ok=True)
        if entry_name is None:
            self.file_path = self._export_path + self._FILENAME_PLAIN
        else:
            self.file_path = (
                self._export_path
                + self._FILENAME_PLAIN
                + self._gen_filename(entry_name.lower())
            )

    def stdout(self) -> None:
        # TODO add columns header
        # TODO add groups
        for entry in self._entries:
            print(
                f"{entry['uuid']}  {entry['type']:5}  {entry['name']:<20}  {entry['issuer']:<20}  {entry['info']['secret']}  {entry['info']['algo']:6}  {entry['info']['digits']:2}  {entry['info'].get('period', '')} {entry['note']}"
            )

    def otpauth(self):
        # FIXME missing header
        path = self.export_path + ".txt"

        for entry in self.entries:
                Lissuer = quote(entry["issuer"])
                Lname = quote(entry["name"])
                Lsecret = quote(entry["info"]["secret"])
                Ldigits = entry["info"]["digits"]
                Lurl = (
                        f"otpauth://totp/{Lissuer}:{Lname}"
                        f"?secret={Lsecret}"
                        f"&digits={Ldigits}"
                        f"&issuer={Lissuer}"
                    )
                #print(Lurl)
                with open(path, "a", encoding="utf-8") as f:
                    f.write(Lurl + "\n")

        print('WARNING! The produced unencrypted TXT.')
        print(f"Entries unencrypted saved as: {path}")

    def csv(self) -> None:
        # TODO add groups
        path = self.file_path + ".csv"
        with io.open(path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            header = [
                "uuid",
                "type",
                "name",
                "issuer",
                "secret",
                "algo",
                "digits",
                "period",
                "note",
            ]
            writer.writerow(header)
            for entry in self._entries:
                writer.writerow(
                    [
                        entry["uuid"],
                        entry["type"],
                        entry["name"],
                        entry["issuer"],
                        entry["info"]["secret"],
                        entry["info"]["algo"],
                        entry["info"]["digits"],
                        entry["info"].get("period", ""),
                        entry['note'],
                    ]
                )

    def otp(self) -> None:
        for entry in self._entries:
            if entry.get("type", "") == "totp":
                totp = EntryTOTP(entry)
                print(
                    f"Entry {entry.get('name', '')} - issuer {entry.get('issuer', '')} - TOTP generated: {totp.generate_code()}"
                )
            else:
                print(
                    f"Entry {entry.get('name', '')} - issuer {entry.get('issuer', '')} - OTP type not supported: {entry.get('type', '')}"
                )

    def json(self) -> None:
        # TODO add aegis headers and groups
        path = self.file_path + ".json"
        with io.open(path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self._entries, indent=4))
            print(
                'WARNING! The produced unencrypted JSON has not the same structure of the Aegis unencrypted export. This JSON contains only the "entries" array.'
            )
            print(f"Unencrypted vault saved as: {path}")

    def qrcode(self) -> None:
        # TODO put all QRcodes in a well formatted PDF
        for entry in self._entries:
            if entry.get("type", "") == "totp":
                totp = EntryTOTP(entry)
                img = totp.generate_qr_code()
                save_filename = (
                    self._export_path
                    + self._gen_filename(entry.get("name"), entry.get("issuer"))
                    + ".png"
                )
                img.png(save_filename, scale=4, background="#fff")
                print(
                    f"Entry {entry.get("name", ""):<25} - Issuer {entry.get("issuer", ""):<25} - TOTP QRCode saved as: {save_filename:<100}"
                )
            else:
                print(
                    f"Entry {entry.get("name", ""):<25} - Issuer {entry.get("issuer", ""):<25} - OTP type not supported: {entry.get("type", ""):<6}"
                )

    def _valid_filename_char(self, c: str) -> bool:
        return c.isalpha() or c.isdigit() or c in "@_-"

    def _gen_filename(self, entry_name: str, entry_issuer: str | None = None) -> str:
        parts = []
        label = entry_name
        if label:
            parts.append(label)
        issuer = entry_issuer
        if issuer:
            parts.append(issuer)

        key = "@".join(parts)

        prefix = "".join([c for c in key if self._valid_filename_char(c)]).strip()

        candidate = f"{prefix}"

        return candidate
