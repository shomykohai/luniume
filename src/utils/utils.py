import os
import hashlib
import base64
import requests
import subprocess
from typing import Dict, List, Union, Final
import orjson

PATCHES_FILE: Final[str] = "patches/patches.json"


def get_global_patches() -> Dict:
    if not os.path.exists(PATCHES_FILE):
        print(f"Global patches file {PATCHES_FILE} not found.")
        return {}
    with open(PATCHES_FILE, "rb") as f:
        return orjson.loads(f.read())

def sri_hash(file_path: str) -> str:
    """Returns the SRI-sha256 hash of a file"""
    with open(file_path, 'rb') as f:
        file_content = f.read()
    hash_digest = hashlib.sha256(file_content).digest()
    return "sha256-" + base64.b64encode(hash_digest).decode('utf-8')


def download_file(url: str, dest: str) -> bool:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(dest, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred while downloading {url}: {e}")
        return False
    else:
        print(f"Downloaded {url} to {dest}")
        return True
    


def run_cli_command(command: List[str]) -> Union[str, None]:
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output_lines = []
    try:
        for line in process.stdout:
            print(line, end='')
            output_lines.append(line)
        process.wait()
        if process.returncode == 0:
            return ''.join(output_lines).strip()
        else:
            print(f"Command failed with exit code {process.returncode}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None

