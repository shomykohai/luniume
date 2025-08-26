import requests
from bs4 import BeautifulSoup
from .generic_downloader import GenericDownloader

HEADERS = {"User-Agent": "Mozilla/5.0"}

class APKMirrorDownloader(GenericDownloader):
    def construct_version_url(self, base_url, version):
        version_slug = version.replace('.', '-')
        return f"{base_url}-{version_slug}-release/"

    def find_download_link(self, version_url):
        r = requests.get(version_url, headers=HEADERS)
        if r.status_code != 200:
            return None, None
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("div.table-row.headerFont")
        for row in rows:
            link = row.find("a", href=True)
            spans = row.find_all("span")[2:]
            if link and len(spans) >= 4:
                type_ = spans[0].text.strip()
                arch = spans[1].text.strip().lower()
                if type_ == "APK" and arch in ("universal", "noarch"):
                    return link["href"], type_
        for row in rows:
            link = row.find("a", href=True)
            spans = row.find_all("span")[2:]
            if link and len(spans) >= 4:
                return link["href"], spans[0].text.strip()
        return None, None

    def resolve_final_url(self, page_url):
        r = requests.get(page_url, headers=HEADERS)
        soup = BeautifulSoup(r.text, "html.parser")
        btn = soup.find("a", class_="btn", href=True)
        if not btn:
            return None
        next_url = btn["href"]
        if next_url.startswith("/"):
            next_url = "https://www.apkmirror.com" + next_url
        r2 = requests.get(next_url, headers=HEADERS)
        soup2 = BeautifulSoup(r2.text, "html.parser")
        a = soup2.find("a", rel="nofollow", href=True)
        if not a:
            return None
        final = a["href"]
        if final.startswith("/"):
            final = "https://www.apkmirror.com" + final
        return final

    def download_apk(self, config: dict, output_path: str, name: str):
        version_url = self.construct_version_url(config["download_url"], config["version"])
        partial_link, filetype = self.find_download_link(version_url)
        if not partial_link:
            return False
        page_url = "https://www.apkmirror.com" + partial_link
        final_url = self.resolve_final_url(page_url)
        if not final_url:
            return False
        ext = ".apk" if filetype == "APK" else ".apkm"
        r = requests.get(final_url, headers=HEADERS, stream=True)
        with open(output_path + ext, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
