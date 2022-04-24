import random
import time
import logging

import httpx


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from helpers.reader import get_containers
from helpers.download import download_client


def downloader():
    with httpx.Client() as client:
        containers = get_containers()
        random.shuffle(containers)
        for (url, hash, directory) in containers:
            download_client(url=url, hash=hash, directory=directory, client=client)


def main():
    start = time.time()
    downloader()
    print(f"downloading took {time.time() - start}")


if __name__ == "__main__":
    main()
