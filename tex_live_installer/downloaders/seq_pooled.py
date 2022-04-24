import time
import logging
from typing import List

import httpx

from tex_live_installer.datastructures.downloadtask import DownloadTask
from tex_live_installer.helpers.download import download_client


logger = logging.getLogger(__name__)


def downloader(containertasks: List[DownloadTask]):
    with httpx.Client() as client:
        for task in containertasks:
            download_client(client=client, task=task)


def main():
    start = time.time()
    downloader()
    print(f"downloading took {time.time() - start}")


if __name__ == "__main__":
    main()
