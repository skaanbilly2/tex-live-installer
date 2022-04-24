import traceback
import pathlib

import httpx
from helpers.hash import sha512
from helpers.archive import extract_data
from helpers.timetracker import TimeTracker


from logging import getLogger

logger = getLogger(__name__)


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
