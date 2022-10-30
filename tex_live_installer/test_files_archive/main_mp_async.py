from queue import Queue
import tarfile
import asyncio
import httpx
import traceback
import time
import logging
import concurrent.futures
import multiprocessing
import pathlib


from helpers.hash import sha512
from helpers.reader import get_containers

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


queue = asyncio.Queue()
loop = asyncio.get_event_loop()


FOLDER = "./tex_output"
BASEURL = "https://mirror.kumi.systems/ctan/systems/texlive/tlnet/archive"
from fs.memoryfs import MemoryFS


def extract_write(name, directory, fs):
    with fs.open(name, "rb") as wf:
        archive = tarfile.TarFile.open(fileobj=wf, mode="r:xz")
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner=numeric_owner) 
            
        
        safe_extract(archive, path=directory)


async def extract_write_worker(queue: Queue, fs):
    logger.critical("extract_write_worker")
    while True:
        try:
            res = await queue.get()
            print(res)
            if res is None:
                return
            (name, directory) = res
            extract_write(name, directory, fs)
            queue.task_done()
        except:
            traceback.print_exc()


async def download(url: str, hash: str, directory: pathlib.Path, out_queue: Queue, fs):
    async with httpx.AsyncClient() as client:
        logger.debug(f"retrieving {url}")
        response = await client.get(url, timeout=10)

        data = response.read()
        logger.debug("hashing")
        hash_message = sha512(data)

        try:
            assert hash_message == hash
            logger.debug("writing archive")
            with fs.open(hash, "wb") as wf:
                wf.write(data)
            await out_queue.put((hash, directory))
            logger.debug(out_queue.qsize())
        except Exception:
            print("EXCPETION")
            traceback.print_exc()


# async def download_worker(in_queue:Queue, pool:Queue):
#     print("download")
#     while not in_queue.empty():
#         (url, hash, directory) = in_queue.get()
#         print( (url, hash, directory))
#         hash = await download(url=url, hash=hash, fs=fs)

#         # put in the queue
#         out_queue.put((hash, directory))


async def downloader(MAX_CPU=2):
    try:
        mem_fs = MemoryFS()

        args = get_containers()[:20]
        args = [
            arg
            + (
                queue,
                mem_fs,
            )
            for arg in args
        ]

        download_tasks = [asyncio.create_task(download(*arg)) for arg in args]
        N_writers = 4
        extract_workers = [
            asyncio.create_task(
                extract_write_worker(
                    queue,
                    mem_fs,
                )
            )
            for _ in range(N_writers)
        ]

        while queue.empty():
            await asyncio.sleep(0.1)
        await queue.join()
        for task in download_tasks:
            task.cancel()
        for task in extract_workers:
            task.cancel()
        await asyncio.wait(download_tasks)

        for _ in range(MAX_CPU):
            await queue.put(None)
        await asyncio.wait(extract_workers)

    except:
        print("EXCEPTION")
        traceback.print_exc()


async def main():
    start_8 = time.time()
    await downloader(8)
    print(f"downloading with 8 took {time.time() - start_8}")
    return
    start_1 = time.time()
    await downloader(1)
    print(f"downloading with 1 took {time.time() - start_1}")


if __name__ == "__main__":
    asyncio.run(main())
