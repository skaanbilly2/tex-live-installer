from fs.memoryfs import MemoryFS
import pathlib
import tarfile
mem_fs = MemoryFS()


def extract_data(hash:str, data:bytes,directory:pathlib.Path):
    with mem_fs.open(hash, "rwb") as wf:
        wf.write(data)
    with mem_fs.open(hash, "rb") as wf:
        archive = tarfile.TarFile.open(fileobj=wf, mode="r:xz")
        archive.extractall(path=directory)

    mem_fs.remove(hash)