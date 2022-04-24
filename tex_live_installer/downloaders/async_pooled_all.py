import asyncio
import logging
from typing import List

import httpx

logger = logging.getLogger(__name__)

from tex_live_installer.helpers.download import download_async_client
from tex_live_installer.datastructures.downloadtask import DownloadTask


async def worker_async(queue, client):
    i = 0

    while True:
        res: DownloadTask = await queue.get()
        if res is None:
            # Notify the queue that the "work item" has been processed.
            return
        logger.debug(i)

        logger.info(res)
        await download_async_client(client=client, task=res)
        queue.task_done()
        i += 1


async def downloader_async(containertasks: List[DownloadTask], max_parrallel_req=8):
    queue = asyncio.Queue()

    for containertask in containertasks:
        await queue.put(containertask)

    # Create three worker tasks to process the queue concurrently.
    async with httpx.AsyncClient() as client:
        tasks = []
        for _ in range(max_parrallel_req):
            task = asyncio.create_task(worker_async(queue, client))
            tasks.append(task)

        # Wait until the queue is fully processed.
        await queue.join()

        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)
