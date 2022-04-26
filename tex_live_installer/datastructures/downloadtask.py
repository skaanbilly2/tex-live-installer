from dataclasses import dataclass
import pathlib


@dataclass
class DownloadTask:
    name: str
    source_url: str
    target_dir: pathlib.Path
    hash: str = None
    size: int = 0

    def to_dict(self):
        return {
            "name": self.name,
            "source_url": self.source_url,
            "target_dir": str(self.target_dir),
            "hash": self.hash,
            "size": self.size,
        }

    def from_dict(dic: dict):
        return DownloadTask(
            name=dic["name"],
            source_url=dic["source_url"],
            target_dir=pathlib.Path(dic["target_dir"]),
            hash=dic["hash"],
            size=dic["size"],
        )
