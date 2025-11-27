import base64
import io
import json

import cryptography
import cryptography.exceptions
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class AegisDB:
    """
    Class to decrypt and search inside the Aegis vault db.
    """

    def __init__(self, db_path, password):
        self.backend = default_backend()
        self.db_path = db_path
        self.entries = self.decrypt_db(password)

    def __die(self, msg, code=1):
        raise Exception(f"{msg}: {code}")

    # decrypt the Aegis vault file to a Python object
    def decrypt_db(self, password):
        with io.open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "header" not in data:
            raise ValueError("'header' key is missing in the JSON file.")

        header = data["header"]

        # extract all password slots from the header
        if not isinstance(header["slots"], list):
            raise ValueError(
                "'slots' key must have a list as its value in the JSON file."
            )

        slots = [slot for slot in header["slots"] if slot["type"] == 1]

        # try the given password on every slot until one succeeds
        master_key = None
        for slot in slots:
            # derive a key from the given password
            kdf = Scrypt(
                salt=bytes.fromhex(slot["salt"]),
                length=32,
                n=slot["n"],
                r=slot["r"],
                p=slot["p"],
                backend=self.backend,
            )
            key = kdf.derive(password)

            # try to use the derived key to decrypt the master key
            cipher = AESGCM(key)
            params = slot["key_params"]
            try:
                master_key = cipher.decrypt(
                    nonce=bytes.fromhex(params["nonce"]),
                    data=bytes.fromhex(slot["key"]) + bytes.fromhex(params["tag"]),
                    associated_data=None,
                )
                break
            except cryptography.exceptions.InvalidTag:
                pass

        if master_key is None:
            raise ValueError("Unable to decrypt the master key with the given password.")

        # decode the base64 vault contents
        content = base64.b64decode(data["db"])

        # decrypt the vault contents using the master key
        if not isinstance(header["params"], dict):
            raise ValueError(
                "'params' key must have a dict as its value in the JSON file."
            )

        params = header["params"]
        cipher = AESGCM(master_key)
        db = cipher.decrypt(
            nonce=bytes.fromhex(params["nonce"]),
            data=content + bytes.fromhex(params["tag"]),
            associated_data=None,
        )

        return json.loads(db.decode("utf-8"))["entries"]

    def get_all(self):
        return self.entries

    def get_by_name(self, name, issuer):
        entries_found = []

        for entry in self.entries:
            db_name = entry.get("name", "")
            db_issuer = entry.get("issuer", "")

            # Looks also for substrings
            if (name is None or name.lower() in db_name.lower()) and (
                issuer is None or issuer.lower() in db_issuer.lower()
            ):
                entries_found.append(entry)

        return entries_found
