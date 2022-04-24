import json
import pathlib

from config import OUTPUT_FOLDER, N_packages, MIRROR_BASE_URL, INPUT_FILE


def get_containers(filename=INPUT_FILE):
    packages_dict = []
    with open(filename) as inputfile:
        packages_dict = json.load(inputfile)

    key_to_suffix = {
        "containerchecksum": "",
        "doccontainerchecksum": ".doc",
        "srccontainerchecksum": ".source",
    }
    container_download = []

    base_folder = pathlib.Path.cwd() / pathlib.Path(OUTPUT_FOLDER)
    for package in packages_dict:
        containerchecksums_keys = [
            key for key in package.keys() if key.endswith("containerchecksum")
        ]
        for key in containerchecksums_keys:
            suffix = key_to_suffix[key]
            url = f'{MIRROR_BASE_URL}/{package["name"]}{suffix}.tar.xz'
            directory = base_folder / str(package["name"] + suffix)
            container_download.append((url, package[key], directory))

    return container_download[:N_packages]
