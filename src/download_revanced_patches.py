from utils.utils import download_file
from utils.github_downloader import GithubReleaseDownloader
import json
import os
import requests
from urllib.parse import urlparse

PATCHES_DIR = "patches/revanced"
PATCHES_JSON = "patches/patches.json"

def main():
    with open(PATCHES_JSON) as f:
        patches = json.load(f)

    downloader = GithubReleaseDownloader()

    for patch_name, patch_info in patches.get("revanced", {}).items():
        repo_url = patch_info["url"]
        version = patch_info.get("version", "latest")
        parts = urlparse(repo_url).path.strip("/").split("/")
        repo = f"{parts[0]}/{parts[1]}"
        asset_name = "*.rvp"
        tag = version
        if version == "latest":
            tag = downloader.get_latest_release_tag(repo)

        asset_url = downloader.get_asset_download_url(repo, tag, asset_name)
        if asset_url:
            print(f"Downloading patch {patch_name} from {asset_url}")
            output_patch = os.path.join(PATCHES_DIR, patch_name + ".rvp")
            download_file(asset_url, output_patch)

if __name__ == "__main__":
    main()