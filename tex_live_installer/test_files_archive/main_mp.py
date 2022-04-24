import multiprocessing
from multiprocessing.pool import AsyncResult
from typing import List
import time
import logging

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)


from helpers.reader import get_containers
from helpers.download import download


def worker(queue):
    logger.info("Starting worker")
    while True:
        res = queue.get()
        if res is None:
            logger.info("Shutting down worker")
            return
        (packagename, hash, directory) = res
        logger.info((packagename, hash, directory))
        download(url=packagename, hash=hash, directory=directory)


def downloader(MAX_CPU=8):
    mgr = multiprocessing.Manager()
    queue = mgr.Queue()

    for container in get_containers():
        queue.put(container)

    with multiprocessing.Pool(MAX_CPU) as pool:
        workers: List[AsyncResult] = []
        for _ in range(MAX_CPU):
            workers.append(pool.apply_async(worker, (queue,)))

        # Wait until the queue is fully processed.
        for _ in range(MAX_CPU):
            queue.put(None)
        for worker_res in workers:
            worker_res.wait()

        pool.close()
        pool.join()


def main():
    start_8 = time.time()
    downloader(8)
    print(f"downloading with 8 took {time.time() - start_8}")

    start_1 = time.time()
    downloader(1)
    print(f"downloading with 1 took {time.time() - start_1}")


if __name__ == "__main__":
    main()
