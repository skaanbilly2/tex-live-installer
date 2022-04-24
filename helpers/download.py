import httpx
import pathlib
import traceback
from helpers.hash import sha512
from helpers.archive import extract_data
import time

from logging import getLogger

logger = getLogger(__name__)


class TimeTracker:
    def __init__(self) -> None:
        self.time = time.time()
        self.tasks = []

    def task_done(self, name):
        new_time = time.time()
        self.tasks.append((new_time - self.time, name))
        self.time = new_time

    def report(self):
        tot_time = sum((time for (time, label) in self.tasks))
        logger.info(f"tot_time: {tot_time}")
        for time, name in self.tasks:
            logger.info(f"task {name} took {100*time/tot_time}% of time")


async def download_async(url: str, hash: str, directory: pathlib.Path):
    tracker = TimeTracker()
    async with httpx.AsyncClient() as client:
        logger.debug(f"retrieving {url}")
        response = await client.get(url)
        data = response.read()
        logger.debug("hashing")
        hash_message = sha512(data)
        tracker.task_done("get response + hash")

        try:
            assert hash_message == hash
            logger.debug("extracting archive")
            extract_data(data, directory)
            tracker.task_done("Extract and write")
            tracker.report()
        except Exception:
            traceback.print_exc()


async def download_async_client(url: str, hash: str, directory: pathlib.Path, client):
    tracker = TimeTracker()
    logger.debug(f"retrieving {url}")
    response = await client.get(url)
    data = response.read()
    logger.debug("hashing")
    hash_message = sha512(data)
    tracker.task_done("get response + hash")

    try:
        assert hash_message == hash
        logger.debug("extracting archive")
        extract_data(data, directory)
        tracker.task_done("Extract and write")
        tracker.report()
    except Exception:
        traceback.print_exc()


async def download_async_multiple(tasks):
    async with httpx.AsyncClient() as client:
        for (url, hash, directory) in tasks:
            tracker = TimeTracker()
            logger.debug(f"retrieving {url}")
            response = await client.get(url)
            data = response.read()
            logger.debug("hashing")
            hash_message = sha512(data)
            tracker.task_done("get response + hash")

            try:
                assert hash_message == hash
                logger.debug("extracting archive")
                extract_data(data, directory)
                tracker.task_done("Extract and write")
                tracker.report()
            except Exception:
                traceback.print_exc()


def download(url: str, hash: str, directory: pathlib.Path):
    tracker = TimeTracker()
    with httpx.Client() as client:
        logger.debug(f"retrieving {url}")
        response = client.get(url)

        data = response.read()
        logger.debug("hashing")
        hash_message = sha512(data)
        tracker.task_done("get response + hash")

        try:
            assert hash_message == hash
            logger.debug("extracting archive")
            extract_data(data, directory)
            tracker.task_done("Extract and write")
            tracker.report()
        except Exception:
            traceback.print_exc()


def download_client(url: str, hash: str, directory: pathlib.Path, client):
    tracker = TimeTracker()
    with httpx.Client() as client:
        logger.debug(f"retrieving {url}")
        response = client.get(url)

        data = response.read()
        logger.debug("hashing")
        hash_message = sha512(data)
        tracker.task_done("get response + hash")

        try:
            assert hash_message == hash
            logger.debug("extracting archive")
            extract_data(data, directory)
            tracker.task_done("Extract and write")
            tracker.report()
        except Exception:
            traceback.print_exc()
