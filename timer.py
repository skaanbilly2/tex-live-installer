import asyncio
from main_async import downloader_async
from main_mp import downloader
import time




def timer(function, arg):
    start = time.time()
    function(arg)
    return time.time() - start


async def timer_async(function, arg):
    start = time.time()
    await function(arg)
    return time.time() - start




async def main():
    args = [i for i in range(1, 50, 5)]
    print(args)
    async_times = {}
    mp_times = {}
    for arg in args:
        print(arg)
        async_times[arg] = await timer_async(downloader_async, arg)
        mp_times[arg] = timer(downloader, arg)

    print("ASYNC")
    print(async_times)
    print("MP")
    print(mp_times)



if __name__ == "__main__":
    asyncio.run(main())