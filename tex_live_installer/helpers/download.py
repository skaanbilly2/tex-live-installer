import traceback
from logging import getLogger

from httpx import AsyncClient, Client

from tex_live_installer.helpers.hash import sha512
from tex_live_installer.helpers.archive import extract_data
from tex_live_installer.helpers.timetracker import TimeTracker
from tex_live_installer.datastructures.downloadtask import DownloadTask

logger = getLogger(__name__)


async def download_async_client(
    client: AsyncClient,
    task: DownloadTask,
):
    tracker = TimeTracker()
    logger.debug(f"retrieving {task.source_url}")
    response = await client.get(task.source_url)
    data = response.read()
    logger.debug("hashing")
    hash_message = sha512(data)
    tracker.task_done("get response + hash")

    try:
        assert hash_message == task.hash
        logger.debug("extracting archive")
        extract_data(data, task.target_dir)
        tracker.task_done("Extract and write")
        tracker.report()
    except Exception:
        traceback.print_exc()


def download_client(client: Client, task: DownloadTask):
    tracker = TimeTracker()
    with Client() as client:
        logger.debug(f"retrieving {task.source_url}")
        response = client.get(task.source_url)

        data = response.read()
        logger.debug("hashing")
        hash_message = sha512(data)
        tracker.task_done("get response + hash")

        try:
            assert hash_message == task.hash
            logger.debug("extracting archive")
            extract_data(data, task.target_dir)
            tracker.task_done("Extract and write")
            tracker.report()
        except AssertionError:
            logger.critical(
                f"{task}: found hash message {repr(hash_message)}, expected hash {repr(task.hash)}"
            )

        except Exception:
            traceback.print_exc()
