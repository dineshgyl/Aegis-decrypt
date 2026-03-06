PS C:\Users\0G2105649\Downloads\Python> & c:/Users/0G2105649/Downloads/Python/.venv/Scripts/python.exe c:/Users/0G2105649/Downloads/Python/Aegis-decrypt/aegis_decrypt.py --vault "C:\Users\0G2105649\Downloads\Python\Aegis-decrypt\aegis-backup-20251127-165400.json" --output csv --password xx
pyinstaller --onefile aegis_decrypt.py        

Due to 
import importlib.metadata
VERSION = importlib.metadata.version("aegis_decrypt")

pip install -e .
python -m aegis_decrypt
