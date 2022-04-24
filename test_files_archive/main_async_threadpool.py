import time
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import concurrent.futures


from helpers.reader import get_containers
from helpers.download import download


def downloader_async(max_parrallel_req=8):
    containers = get_containers()
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_parrallel_req
    ) as executor:
        futures = {executor.submit(download(*container)) for container in containers}
        for future in futures:
            print(future.result())


def main():
    start_1 = time.time()
    downloader_async(8)
    print(f"downloading with 1 took {time.time() - start_1}")


if __name__ == "__main__":
    main()
