import pyotp
import pyqrcode
from pyqrcode import QRCode

import hashlib

class EntryTOTP:
    """
    Class to handle the TOTP generation.
    """

    _HASHLIB_ALGO_MAP = {
        "SHA1":   hashlib.sha1,
        "SHA256": hashlib.sha256,
        "SHA512": hashlib.sha512,
        "MD5":    hashlib.md5,
    }

    def __init__(self, entry):
        self._entry = entry
        self._totp = pyotp.TOTP(
            s=entry["info"]["secret"],
            digits=entry["info"]["digits"],
            digest=self._resolve_hash_algo(entry["info"]["algo"]),
            name=entry["name"],
            issuer=entry["issuer"],
            interval=entry["info"]["period"]
        )

    def generate_code(self) -> str:
        """
        Generate the current TOTP code
        """
        return self._totp.now()

    def generate_otpauthurl(self) -> str:
        """
        Generate the otpauth url for the current TOTP entry
        """
        url = self._totp.provisioning_uri(
            self._entry["name"], issuer_name=self._entry["issuer"]
        )
        if url:
            return url
        raise Exception(
            f"Unable to generate otpauth url for entry {self._entry['name']} with issuer {self._entry['issuer']}"
        )

    def generate_qr_code(self) -> QRCode:
        """
        Generate the QR Code for the current TOTP entry
        """
        url = self._totp.provisioning_uri(
            self._entry["name"], issuer_name=self._entry["issuer"]
        )
        if url:
            return pyqrcode.create(url)
        raise Exception(
            f"Unable to generate QR Code for entry {self._entry['name']} with issuer {self._entry['issuer']}"
        )

    def _resolve_hash_algo(self, algo: str):
        """
        Map an Aegis ``entry["info"]["algo"]`` value to the matching
        hashlib constructor (e.g. ``hashlib.sha1``).
        Raises ValueError for unsupported algorithms.
        """
        try:
            return self._HASHLIB_ALGO_MAP[algo.upper()]
        except KeyError as exc:
            raise ValueError(f"Unsupported hash algorithm: {algo!r}") from exc