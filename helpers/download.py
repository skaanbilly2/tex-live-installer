import httpx
import pathlib
import traceback
from helpers.hash import sha512
from helpers.archive import extract_data
from httpx import AsyncClient, Client


from logging import getLogger

logger = getLogger(__name__)

from timetracker import TimeTracker


async def download_async_client(
    client: AsyncClient, url: str, hash: str, directory: pathlib.Path
):
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


def download_client(client: Client, url: str, hash: str, directory: pathlib.Path):
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
