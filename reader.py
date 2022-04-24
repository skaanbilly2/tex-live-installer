import json
import pathlib

FOLDER  = "F:/tex_output"
BASEURL = "https://mirror.kumi.systems/ctan/systems/texlive/tlnet/archive"
N = 300

def get_containers(filename = "input.json"):
    packages_dict = []
    with open("input.json") as inputfile:
        packages_dict = json.load(inputfile) 

    key_to_suffix = {
        "containerchecksum": "",
        "doccontainerchecksum": ".doc",
        "srccontainerchecksum": ".source"
    }
    container_download = []

    base_folder = pathlib.Path.cwd() / pathlib.Path(FOLDER)
    for package in packages_dict:
        containerchecksums_keys = [key for key in package.keys() if key.endswith("containerchecksum")]
        for key in containerchecksums_keys:
            suffix = key_to_suffix[key]
            url = f'{BASEURL}/{package["name"]}{suffix}.tar.xz'
            directory = base_folder / str(package["name"] + suffix)
            container_download.append((url, package[key], directory))
    
    return container_download[:N]