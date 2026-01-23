import pyotp
import pyqrcode
from pyqrcode import QRCode


class EntryTOTP:
    """
    Class to handle the TOTP generation.
    """

    def __init__(self, entry):
        self._entry = entry
        self._totp = pyotp.TOTP(
            entry["info"]["secret"], interval=entry["info"]["period"]
        )

    def generate_code(self) -> str:
        """
        Generate the current TOTP code
        """
        return self._totp.now()

    def generate_qr_code(self) -> QRCode:
        """
        Generate the QR Code for the current TOTP entry
        """
        url = self._totp.provisioning_uri(
            self._entry["name"], issuer_name=self._entry["issuer"]
        )
        if url:
            return pyqrcode.create(url)
        raise Exception(f"Unable to generate QR Code for entry {self._entry["name"]} with issuer {self._entry['issuer']}")
