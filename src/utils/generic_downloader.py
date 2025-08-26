from abc import ABC, abstractmethod

class GenericDownloader(ABC):
    @abstractmethod
    def download_apk(self, config: dict, output_path: str, name: str) -> bool:
        pass
