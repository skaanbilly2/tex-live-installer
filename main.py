import argparse, argcomplete
import logging
import asyncio
import random
import pathlib
import json
import time
from tex_live_installer.datastructures.downloadtask import DownloadTask

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from tex_live_installer.helpers.reader import get_containers
from tex_live_installer.helpers.extract import extract_file
from tex_live_installer.downloaders.async_pooled_all import downloader_async
from tex_live_installer.downloaders.seq_pooled import downloader
from tex_live_installer.helpers.timetracker import TimeTracker

DEFAULT_CONFIG_FILES = {
    "install": "config_install.json",
    "install_containers": "config_install_containers.json",
    "extract_tlpdb": "config_extract.json",
}

DEFAULT_CONTAINER_FILE = "containertasks.json"


async def time_function(func, args, asynchronous: bool = False, message: str = ""):
    start = time.time()
    if asynchronous == True:
        await func(*args)
    else:
        func(*args)
    logger.info(f"{message} took {time.time() - start} seconds")


def update_args_from_configfile(args: argparse.Namespace):
    # Use the configs given in the configfile as a default
    with open(args.configfile, "r") as f:
        config_defaults = json.load(f)
        cli_dict = {
            key: value
            for key, value in vars(args).items()
            if value is not None or key not in config_defaults
        }
        new_dict = {**config_defaults, **cli_dict}

        return argparse.Namespace(**new_dict)


async def main():
    parser = argparse.ArgumentParser("python main.py")
    parser.add_argument(
        "command", type=str, choices=("extract_tlpdb", "install", "install_containers")
    )

    ## FILE / LOCATION OPTIONS
    parser.add_argument("--configfile", type=str, help="configfile", default=None)
    parser.add_argument("--inputfile", type=str, help="input file", default=None)
    parser.add_argument(
        "--installdir",
        type=str,
        help="The directory where the packages will be installed.",
        default=None,
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        help="outputfile in case of extract command",
        default=None,
    )
    parser.add_argument(
        "--mirror_base_url",
        type=str,
        help="The base url to fetch archives from",
        default=None,
    )

    ## TEST OPTION
    parser.add_argument(
        "--n_containers",
        type=int,
        help="Limits the number of installed packages to the first N",
        default=None,
    )

    # Random shuffle for amortising large packages, disable for accurate performance result samples
    # TODO enable for production
    parser.add_argument(
        "--reshuffle",
        type=str,
        help="Reshuffles the containers to spread large containers evenly",
        choices=("True", "False"),
        default="False",
    )

    ## ASYNC OPTIONS
    parser.add_argument(
        "--asyncio",
        type=str,
        help="Enables the asynchronous install mode",
        choices=("True", "False"),
        default="False",
    )
    parser.add_argument(
        "--n_workers",
        help="number of threads ( 1 GIL For more info see https://realpython.com/python-gil/#:~:text=The%20Python%20Global%20Interpreter%20Lock%20or%20GIL%2C%20in%20simple%20words,at%20any%20point%20in%20time. )",
        type=int,
        default=1,
    )

    argcomplete.autocomplete(parser)
    args = parser.parse_args()

    if args.configfile is None:
        args.configfile = DEFAULT_CONFIG_FILES[args.command]

    args = update_args_from_configfile(args)

    if args.command == "extract_tlpdb":
        extract_file(
            infile=pathlib.Path(args.inputfile), outfile=pathlib.Path(args.outputfile)
        )
    elif args.command == "install" or args.command == "install_containers":
        args.asyncio = args.asyncio == ("True")

        containertasks = []
        if args.command == "install_containers":
            if args.inputfile is None:
                args.inputfile = DEFAULT_CONTAINER_FILE
            with open(args.inputfile, "r") as f:
                containertasks = json.load(f)
                containertasks = [
                    DownloadTask.from_dict(task_dict) for task_dict in containertasks
                ]
        else:
            containertasks = get_containers(
                filepath=pathlib.Path(args.inputfile),
                mirror_url=args.mirror_base_url,
                output_folder=pathlib.Path(args.installdir),
            )
        if False:
            json_containertasks = [task.to_dict() for task in containertasks[0:20]]
            with open(DEFAULT_CONTAINER_FILE, "w") as f:
                json.dump(json_containertasks, f)

        if args.reshuffle == "True":
            random.shuffle(containertasks)
        if args.n_containers is None:
            args.n_containers = len(containertasks)

        containertasks = containertasks[: min(len(containertasks), args.n_containers)]

        if args.asyncio:
            await time_function(
                downloader_async,
                (
                    containertasks,
                    args.n_workers,
                ),
                asynchronous=args.asyncio,
                message=f"Asynchronous download of selected {args.n_containers} containers with {args.n_workers} worker ",
            )
        else:
            await time_function(
                downloader,
                (containertasks,),
                message=f"Synchronous download of selected {args.n_containers} containers ",
            )

        # Save timetracker data
        with open("timings.json", "w") as f:
            json.dump(TimeTracker.time_measurements, f)


if __name__ == "__main__":
    asyncio.run(main())
