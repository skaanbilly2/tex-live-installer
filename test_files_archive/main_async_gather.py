import asyncio
import time
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


from reader import get_containers
from download import download_async, download_async_multiple


from fs.memoryfs import MemoryFS
mem_fs = MemoryFS()
import httpx



        

async def worker_async(queue):
    i = 0
    while True:
        async with httpx.AsyncClient() as client:
            res = await queue.get()
            if res is None:
                # Notify the queue that the "work item" has been processed.
                return
            logger.debug(i)
            (packagename, hash, directory) = res
            
            logger.info((packagename, hash, directory))
            await download_async(url=packagename, hash=hash, directory=directory, client=client)
            queue.task_done()
            i += 1
        



async def downloader_async():
    containers = get_containers()
    tasks = [download_async_multiple(*container) for container in containers]

    await asyncio.gather(*tasks)


async def main():
    start_1 = time.time()
    await downloader_async()
    print(f"downloading with 1 took {time.time() - start_1}")

    # start_8 = time.time()
    # await downloader(8)
    # print(f"downloading with 8 took {time.time() - start_8}")

    # start_20 = time.time()
    # await downloader(20)
    # print(f"downloading with 20 took {time.time() - start_20}")

    # start_50 = time.time()
    # await downloader(50)
    # print(f"downloading with 20 took {time.time() - start_50}")


if __name__ == "__main__":
    asyncio.run(main())