import os
import orjson
from abc import ABC, abstractmethod
from utils import get_downloader
from typing import Final, List
from utils.utils import run_cli_command

APPS_DIR: Final[str] = "apps"

class Keystore():
    def __init__(self, path: str, password: str, alias: str, alias_password: str):
        self.path: Final[str] = path
        self.password: Final[str] = password
        self.alias: Final[str] = alias
        self.alias_password: Final[str] = alias_password

    def __repr__(self):
        return f"Keystore(path={self.path})"

class App():
    def __init__(self, name: str, path: str):
        self.name: Final[str] = name
        self.path: Final[str] = path
        self.config = self.load_config()

    @property
    def package_name(self) -> str:
        return self.config.get("package_name", "")
    
    @property
    def patch_method(self) -> str:
        return self.config.get("patch_method", "default")

    @property
    def patches(self) -> List[str]:
        return self.config.get("patches", [])

    @property
    def is_split(self) -> bool:
        return self.config.get("split", False)

    @property
    def is_downloaded(self) -> bool:
        if os.path.exists(f"tmp/{self.package_name}.apk"):
            return True
        return os.path.exists(f"tmp/{self.package_name}.apkm")  

    def merge(self) -> bool:
        if not self.is_split:
            return True

        apk_path = f"tmp/{self.package_name}.apk"
        apkm_path = f"tmp/{self.package_name}.apkm"

        if not os.path.exists(apkm_path):
            return True

        if os.path.exists(apk_path):
            os.remove(apk_path)

        print(f"App {self.name} is split, merging APKs.")
        command = ["APKEditor", "merge", "-i", apkm_path, "-o", apk_path]
        run_cli_command(command)

        os.remove(apkm_path)

        return True


    def download(self) -> None:
        ext = "apkm" if self.is_split else "apk"
        download_path = os.path.join("tmp", f"{self.package_name}")

        if not self.is_downloaded:
            print(f"Downloading {self.name} to {download_path}.{ext}")
            source = self.config.get("source", "apkmirror")
            downloader = get_downloader(source)
            success = downloader.download_apk(self.config, download_path, self.name)
            if not success:
                print(f"Failed to download {self.name}.")
        else:
            print(f"{self.name} is already downloaded at tmp/{self.package_name}.{ext}")

        if self.is_split:
            self.merge()    

    def load_config(self) -> dict:
        if not os.path.exists(self.path):
            return {}
        with open(self.path, 'r') as f:
            return orjson.loads(f.read())

    def __repr__(self):
        return f"App(name={self.name}, path={self.path})"


class Patch(ABC):
    def __init__(self, app: App, keystore: dict):
        self.app = app
        self.keystore = Keystore(
            path=keystore.get("path", ""),
            password=keystore.get("password", ""),
            alias=keystore.get("alias", ""),
            alias_password=keystore.get("alias_password", "")
        )

    @abstractmethod
    def should_patch(self) -> bool:
        """Determine if the patch should be applied to the app."""
        pass
    
    @abstractmethod
    def apply_patch(self) -> None:
        """Apply the patch to the app. Implement this method in a particular Patch type"""
        pass
    
    def is_keystore_valid(self) -> bool:
        """Self explanatory ._."""
        return all([
            self.keystore.path,
            self.keystore.password,
            self.keystore.alias,
            # self.keystore.alias_password
        ])