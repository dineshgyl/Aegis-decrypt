# Aegis-decrypt
A backup decryptor and OTP generator for the vault of the [Aegis Authenticator](https://getaegis.app/) Android app, inspired by [asmw/andOTP-decrypt](https://github.com/asmw/andOTP-decrypt). It allows to decrypt the Aegis vault and export its values in different unencrypted formats (stdout, CSV, QRCode, Json). It also allows to generate TOTP codes on the fly (HOTP/Stream not supported).

:warning: The project is in active development. See below for [some ideas to implement](#Contributing). :warning:

[![](https://img.shields.io/static/v1?label=Codeberg&message=Aegis-decrypt&style=for-the-badge&logo=codeberg)](https://codeberg.org/scollovati/Aegis-decrypt)
[![](https://img.shields.io/static/v1?label=Gitlab&message=Aegis-decrypt&style=for-the-badge&logo=gitlab)](https://gitlab.com/scollovati/Aegis-decrypt)
[![](https://img.shields.io/static/v1?label=Github&message=Aegis-decrypt&style=for-the-badge&logo=github)](https://github.com/scollovati/Aegis-decrypt)
## Usage
After installing it with Poetry, run `poetry run python aegis_decrypt.py -h`.

The output is:
```
usage: aegis_decrypt.py [-h] [--vault VAULT] [--entryname ENTRYNAME] [--issuer ISSUER] [--search SEARCH] [--output {csv,qrcode,json,otp,stdout,otpauth}] [--password PASSWORD]
                        [--license]

Decrypt an Aegis vault and produce an output as requested. Exported and unencrypted files are placed in a folder `export/` created inside the folder where the vault is.

options:
  -h, --help            show this help message and exit
  --vault VAULT         The encrypted Aegis vault file or a folder containing only Aegis vault files. If it is a folder, the most recent file is considered.
  --entryname ENTRYNAME
                        The name of the entry for which you want to generate the output.
  --issuer ISSUER       The name of the issuer for which you want to generate the output.
  --search SEARCH       Search for a string in all fields of all entries including the note field.
  --output {csv,qrcode,json,otp,stdout,otpauth}
                        The output format. OTP generation is supported only for TOTP protocol. Default: otp
  --password PASSWORD   The encryption password.
  --license             Show license file.
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
- Build Executable `pyinstaller --onefile aegis_decrypt.py`

## Project Management
Since this repo is spread across several remotes, it may happen that there are some pull/merge requests that need to be handled locally.
- If not already done, add the remote repository `REMOTE-URL` with a meaningful `REMOTE-NAME`: `git remote add REMOTE-NAME REMOTE-URL`
- Create a local `BRANCH-NAME` from the pull/merge request `ID`: 
  - Github or Codeberg PR: `git fetch REMOTE-NAME pull/ID/head:BRANCH-NAME`
  - Gitlab MR: `git fetch REMOTE-NAME merge_request/ID/head:BRANCH-NAME`
- Check the branch out: `git checkout BRANCH-NAME`

## Contributing
Contributions are welcome. Some ideas to implement:
- filter outputs by groups
- cool terminal output as a nice table
- export QRCodes in a unique PDF or HTML (simple paper backup)
- export CSV in a KeepassXC compatible format for importing TOTP to that database
- support for HOTP/Steam format
- install this script as a system tool
- save and remove password from OS keychain, MacOS TouchId, ...

## Contributors
- [asmw](https://github.com/asmw): original andOTP-decrypt repository on GitHub
- [scollovati](https://gitlab.com/scollovati/): forked andOTP-decrypt and setup the Aegis-decrypt project
- [kvngvikram](https://github.com/kvngvikram)
- [combolek](https://github.com/combolek)
- [juergenhoetzel](https://github.com/juergenhoetzel)
- [dineshgyl](https://github.com/dineshgyl)