import re
import requests
from .generic_downloader import GenericDownloader

HEADERS = {"User-Agent": "Mozilla/5.0"}

class GithubReleaseDownloader(GenericDownloader):
    def get_latest_release_tag(self, repo: str) -> str:
        api_url = f"https://api.github.com/repos/{repo}/releases/latest"
        resp = requests.get(api_url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        return data.get("tag_name", "")

    def get_asset_download_url(self, repo: str, tag: str, asset_name: str) -> str:
        api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
        resp = requests.get(api_url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        assets = data.get("assets", [])

        for asset in assets:
            name = asset["name"]
            if asset_name == name or (
                "*" in asset_name and self.asset_match(asset_name, name)
            ):
                return asset["browser_download_url"]
        return ""

    def asset_match(self, pattern: str, name: str) -> bool:
        regex_pattern = re.escape(pattern).replace(r'\*', '.*')
        regex_pattern = f"^{regex_pattern}$"
        return re.match(regex_pattern, name) is not None

    def download_apk(self, config: dict, output_path: str, name: str) -> bool:
        repo = config.get("repo", "")
        version = config.get("version", "latest")
        asset_name = config.get("asset_name", "*.apk")

        if not repo:
            print("GitHub repo not specified in config.")
            return False

        tag = version
        if version == "latest":
            try:
                tag = self.get_latest_release_tag(repo)
            except Exception as e:
                print(f"Failed to fetch latest release tag: {e}")
                return False

        try:
            asset_url = self.get_asset_download_url(repo, tag, asset_name)
        except Exception as e:
            print(f"Failed to get asset download URL: {e}")
            return False

        if not asset_url:
            print(f"Asset '{asset_name}' not found in release '{tag}' for repo '{repo}'.")
            return False

        try:
            r = requests.get(asset_url, headers=HEADERS, stream=True)
            r.raise_for_status()
            with open(output_path + ".apk", "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"Downloaded {asset_url} to {output_path}.apk")
            return True
        except Exception as e:
            print(f"Failed to download asset: {e}")
            return False