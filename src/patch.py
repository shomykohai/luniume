import argparse
import orjson
import os
import subprocess
import requests
from abc import ABC, abstractmethod
from typing import Final, List, Optional, Union, Dict
from utils import get_downloader



from utils.utils import get_global_patches
APPS_DIR: Final[str] = "apps"
from patchers import LSPatch, App, RevancedPatch


PATCHERS_MAP: Final[Dict[str, type]] = {
    "lspatch": LSPatch,
    "revanced": RevancedPatch,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Patch apps with global patches.")
    parser.add_argument("app_name", type=str, help="Name of the app to patch")
    
    parser.add_argument("--keystore-path", type=str, help="Path to keystore file")
    parser.add_argument("--keystore-password", type=str, help="Keystore password")
    parser.add_argument("--keystore-alias", type=str, help="Keystore alias")

    
    args = parser.parse_args()

    app_path = os.path.join(APPS_DIR, f"{args.app_name}.json")
    if not os.path.exists(app_path):
        print(f"App configuration file {app_path} not found.")
        exit(1)

    global_patches: Dict = get_global_patches()
    app = App(args.app_name, app_path)
    
    keystore = {
        "path": args.keystore_path,
        "password": args.keystore_password,
        "alias": args.keystore_alias,
    }
    if all(keystore.values()):
        print("Using custom keystore.")

    patch = PATCHERS_MAP.get(app.patch_method)(app, keystore)

    if patch.should_patch():
        patch.apply_patch()
    else:
        print(f"No applicable patches for {app.name}.") 

 