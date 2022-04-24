import pathlib
import tarfile
import io


def extract_data(data: bytes, directory: pathlib.Path):
    buf = io.BytesIO(initial_bytes=data)

    archive = tarfile.TarFile.open(fileobj=buf, mode="r:xz")
    archive.extractall(path=directory)
