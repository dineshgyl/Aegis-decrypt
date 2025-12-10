import base64
import io
import json
import os

import cryptography
import cryptography.exceptions
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt


class AegisDB:
    """
    Class to decrypt and search inside the Aegis vault db.
    """

    def __init__(self, db_path: str, password: str):
        """
        db_path and password: used for both encryption and decryption.
        """
        self._backend = default_backend()
        self._db_path = db_path
        self._password = password.encode("utf-8")

    def encrypt(self, entries: dict) -> None:
        """
        Encrypts the given entries into an Aegis vault file at db_path.
        """

        # 1. Generate a random Master Key (32 bytes for AES-256)
        master_key = os.urandom(32)

        # 2. Encrypt the Database Content
        # The vault content is a JSON object wrapping the entries list
        payload = json.dumps({"entries": entries}).encode("utf-8")

        # AES-GCM encrypts payload using the Master Key
        cipher_db = AESGCM(master_key)
        nonce_db = os.urandom(12)
        # encrypt returns ciphertext + tag
        encrypted_db = cipher_db.encrypt(nonce_db, payload, None)

        # Split ciphertext and tag (last 16 bytes)
        tag_db = encrypted_db[-16:]
        ciphertext_db = encrypted_db[:-16]

        # 3. Create a Password Slot (Type 1) to protect the Master Key
        # Derive a key from the user password using Scrypt
        salt = os.urandom(32)
        n, r, p = 16384, 8, 1  # Standard Aegis Scrypt parameters

        kdf = Scrypt(
            salt=salt,
            length=32,
            n=n,
            r=r,
            p=p,
            backend=self._backend,
        )
        derived_key = kdf.derive(self._password)

        # Encrypt the Master Key using the derived key
        cipher_key = AESGCM(derived_key)
        nonce_key = os.urandom(12)
        encrypted_master_key = cipher_key.encrypt(nonce_key, master_key, None)

        tag_key = encrypted_master_key[-16:]
        ciphertext_key = encrypted_master_key[:-16]

        # 4. Construct the Vault JSON structure
        vault_data = {
            "version": 1,
            "header": {
                "slots": [
                    {
                        "type": 1,
                        "salt": salt.hex(),
                        "n": n,
                        "r": r,
                        "p": p,
                        "key": ciphertext_key.hex(),
                        "key_params": {"nonce": nonce_key.hex(), "tag": tag_key.hex()},
                    }
                ],
                "params": {"nonce": nonce_db.hex(), "tag": tag_db.hex()},
            },
            "db": base64.b64encode(ciphertext_db).decode("utf-8"),
        }

        with io.open(self._db_path, "w", encoding="utf-8") as f:
            json.dump(vault_data, f, indent=4)

    # decrypt the Aegis vault file to a Python object
    def decrypt(self) -> dict:
        with io.open(self._db_path, "r", encoding="utf-8") as f:
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
                backend=self._backend,
            )
            key = kdf.derive(self._password)

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
            raise ValueError(
                "Unable to decrypt the master key with the given password."
            )

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

        return json.loads(db.decode("utf-8"))

    def get_all(self) -> dict:
        return self.decrypt()["entries"]

    def get_groups(self) -> dict:
        return self.decrypt()["groups"]

    def get_group_by_uuid(self, uuid: str) -> str:
        return self.get_groups().get(uuid, "GROUP NOT FOUND")

    def get_by_name(self, name: str, issuer: str) -> dict:
        entries_found = {}

        for entry in self.get_all():
            db_name = entry.get("name", "")
            db_issuer = entry.get("issuer", "")

            # Looks also for substrings
            if (name is None or name.lower() in db_name.lower()) and (
                issuer is None or issuer.lower() in db_issuer.lower()
            ):
                entries_found.update(entry)

        return entries_found

    def get_db_path(self) -> str:
        return self._db_path