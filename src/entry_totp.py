import time
from datetime import datetime
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

    def get_time_remaining(self) -> int:
        """
        Get the number of seconds remaining until the current TOTP expires
        """
        current_time = int(time.time())
        period = self._entry["info"]["period"]
        return period - (current_time % period)

    def get_next_code(self) -> str:
        """
        Generate the next TOTP code (after current one expires)
        """
        current_time = int(time.time())
        period = self._entry["info"]["period"]
        # Calculate time for next period
        next_period_time = current_time + (period - (current_time % period))
        return self._totp.at(next_period_time)

    def get_current_timestamp(self) -> str:
        """
        Get current timestamp in readable format
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_current_expiry_timestamp(self) -> str:
        """
        Get timestamp when current TOTP expires
        """
        current_time = int(time.time())
        period = self._entry["info"]["period"]
        expiry_time = current_time + (period - (current_time % period))
        return datetime.fromtimestamp(expiry_time).strftime("%Y-%m-%d %H:%M:%S")

    def get_next_expiry_timestamp(self) -> str:
        """
        Get timestamp when next TOTP expires
        """
        current_time = int(time.time())
        period = self._entry["info"]["period"]
        time_remaining = period - (current_time % period)
        next_expiry_time = current_time + time_remaining + period
        return datetime.fromtimestamp(next_expiry_time).strftime("%Y-%m-%d %H:%M:%S")

    def get_progress_bar(self) -> str:
        """
        Get a visual progress bar showing time elapsed (1 character per second)
        █ = 1 second elapsed, ░ = 1 second remaining
        """
        time_remaining = self.get_time_remaining()
        period = self._entry["info"]["period"]
        
        # Each character represents 1 second
        # filled (█) = time elapsed, empty (░) = time remaining
        elapsed = period - time_remaining
        remaining = time_remaining
        
        # Use block characters for progress bar
        bar = "█" * elapsed + "░" * remaining
        return f"[{bar}]"
