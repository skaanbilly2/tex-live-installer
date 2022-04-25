from typing import List
import json
import pathlib

from tex_live_installer.datastructures.downloadtask import DownloadTask


def get_containers(
    filepath: pathlib.Path, mirror_url: str, output_folder: pathlib.Path
) -> List[DownloadTask]:
    packages_dict = []
    with open(filepath) as inputfile:
        packages_dict = json.load(inputfile)

    key_to_suffix = {
        "containerchecksum": "",
        "doccontainerchecksum": ".doc",
        "srccontainerchecksum": ".source",
    }
    container_download = []

    base_folder = pathlib.Path.cwd() / pathlib.Path(output_folder)
    for package in packages_dict:
        containerchecksums_keys = [
            key for key in package.keys() if key.endswith("containerchecksum")
        ]
        for key in containerchecksums_keys:
            suffix = key_to_suffix[key]
            containername = f"{package['name']}{suffix}"
            sizekey = key[:key.index("checksum")] + "size"
            url = f"{mirror_url}/{containername}.tar.xz"
            directory = base_folder / containername
            container_download.append(
                DownloadTask(
                    name=containername,
                    source_url=url,
                    target_dir=directory,
                    hash=package[key],
                    size=package[sizekey]
                )
            )

    return container_download
