# Aegis-decrypt
A backup decryptor and OTP generator for the vault of the [Aegis Authenticator](https://github.com/beemdevelopment/Aegis/) Android app, inspired by [asmw/andOTP-decrypt](https://github.com/asmw/andOTP-decrypt). It allows to decrypt the Aegis vault and export its values in different formats (stdout, CSV, QRCode, Json). It allows to generate TOTP codes on the fly.

:warning: Currently, it supports only TOTP tokens.
:warning: A few improvements are in progress:
- export QRCodes in a unique PDF or HTML (simple paper backup)
- support for HOTP format

[![](https://img.shields.io/static/v1?label=Gitlab&message=Aegis-decrypt&style=for-the-badge&logo=gitlab)](https://gitlab.com/scollovati/Aegis-decrypt)
[![](https://img.shields.io/static/v1?label=Codeberg&message=Aegis-decrypt&style=for-the-badge&logo=codeberg)](https://codeberg.org/scollovati/Aegis-decrypt)
[![](https://img.shields.io/static/v1?label=Github&message=Aegis-decrypt&style=for-the-badge&logo=github)](https://github.com/scollovati/Aegis-decrypt)
## Usage
After installing it with Poetry, run ```bash poetry run python aegis_decrypt.py -h```.

The output is:
```
usage: aegis_decrypt.py [-h] --vault VAULT [--entryname ENTRYNAME] [--issuer ISSUER] [--output {csv,qrcode,json,otp,stdout}] [--password PASSWORD]

Decrypt an Aegis vault and produce an output as requested. Exported files are created in the folder `./export/` inside the project itself.

options:
  -h, --help            show this help message and exit
  --vault VAULT         The encrypted Aegis vault file or a folder containing only Aegis vault files. If it is a folder, the most recent file is considered.
  --entryname ENTRYNAME
                        The name of the entry for which you want to generate the OTP code.
  --issuer ISSUER       The name of the issuer for which you want to generate the OTP code.
  --output {csv,qrcode,json,otp,stdout}
                        The output format. Default: otp
  --password PASSWORD   The encryption password
```

## Development Setup

- Install [Poetry](https://python-poetry.org/docs/#installation)  (recommended)
- Install the package: `poetry install`
- Run the program : `poetry run python aegis_decrypt.py [args]` or `poetry run aegis_decrypt [args]`
- Update dependencies: `poetry update`
- Execute Bandit `poetry run bandit -c pyproject.toml -r .`
- Execute Black `poetry run black .`
- Execute MyPy `poetry run mypy .`
- Execute Pylint `poetry run pylint aegis_decrypt.py src/`

## Project Management
Since this repo is spread across several remotes, it may happen that there are some pull/merge request need to be handled locally.
- Add the remote repository URL with a meaningful NAME: `git remote add REMOTE-NAME REMOTE-URL`
- Create a local BRANCH name from the GitHub pull request ID: `git fetch REMOTE-NAME pull/$ID/head:$BRANCHNAME`

## Contributors
- [asmw](https://github.com/asmw): original andOTP-decrypt repository on GitHub
- [scollovati](https://gitlab.com/scollovati/): forked andOTP-decrypt and setup the Aegis-decrypt project
- [kvngvikram](https://github.com/kvngvikram)
- [combolek](https://github.com/combolek)
- [juergenhoetzel](https://github.com/juergenhoetzel)