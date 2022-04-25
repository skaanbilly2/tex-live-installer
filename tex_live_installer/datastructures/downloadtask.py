from dataclasses import dataclass
import pathlib


@dataclass
class DownloadTask:
    name: str
    source_url: str
    target_dir: pathlib.Path
    hash: str = None
    size:int = 0