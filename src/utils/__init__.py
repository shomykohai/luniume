from .apkm_downloader import APKMirrorDownloader
from .github_downloader import GithubReleaseDownloader
from .generic_downloader import GenericDownloader

def get_downloader(source: str) -> GenericDownloader:
    if source == "apkmirror":
        return APKMirrorDownloader()
    elif source == "github":
        return GithubReleaseDownloader()
    else:
        raise ValueError(f"Unknown source type: {source}")