import tarfile
import hashlib
import pathlib

from fs.memoryfs import MemoryFS
mem_fs = MemoryFS()

def sha512(data):
    h = hashlib.new('sha512')
    h.update(data)
    return h.hexdigest()

def main():
    a = tarfile.open("12many.tar.xz", mode="r:xz")
    print(a.getnames())
    with open("12many.tar.xz", "rb") as infile:
        data = infile.read()
        print(sha512(data))
        with mem_fs.open("many.tar.xz", "rwb") as wf:
            wf.write(data)

        with mem_fs.open("many.tar.xz", "rb") as wf:
            archive = tarfile.TarFile.open(fileobj=wf, mode="r:xz")
            archive.extractall(path=pathlib.Path("./output"))

if __name__ == "__main__":
    main()