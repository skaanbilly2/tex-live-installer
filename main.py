import argparse, argcomplete
import logging
import asyncio
import random
import pathlib
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from tex_live_installer.helpers.reader import get_containers
from tex_live_installer.helpers.extract import extract_file
from tex_live_installer.downloaders.async_pooled_all import downloader_async
from tex_live_installer.downloaders.seq_pooled import downloader

DEFAULT_CONFIG_FILE_INSTALL = "config_install.json"
DEFAULT_CONFIG_FILE_EXTRACT = "config_extract.json"


def update_args_from_configfile(args: argparse.Namespace):
    # Use the configs given in the configfile as a default
    with open(args.configfile, "r") as f:
        config_defaults = json.load(f)
        not_None_dict = {
            key: value for key, value in vars(args).items() if value is not None
        }
        new_dict = {**config_defaults, **not_None_dict}
        args = argparse.Namespace(**new_dict)
        return args


async def main():
    parser = argparse.ArgumentParser("python main.py")
    parser.add_argument("command", type=str, choices=("extract_tlpdb", "install"))

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
        "--n_packages",
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

    if args.command == "extract_tlpdb":
        if args.configfile is None:
            args.configfile = DEFAULT_CONFIG_FILE_EXTRACT
        args = update_args_from_configfile(args)
        extract_file(
            infile=pathlib.Path(args.inputfile), outfile=pathlib.Path(args.outputfile)
        )
    elif args.command == "install":
        if args.configfile is None:
            args.configfile = DEFAULT_CONFIG_FILE_INSTALL
        args = update_args_from_configfile(args)

        containertasks = get_containers(
            filepath=pathlib.Path(args.inputfile),
            mirror_url=args.mirror_base_url,
            output_folder=pathlib.Path(args.installdir),
        )

        if args.reshuffle == "True":
            random.shuffle(containertasks)
        containertasks = containertasks[: min(len(containertasks), args.n_packages)]
        if args.asyncio == "True":
            await downloader_async(containertasks, max_parrallel_req=args.n_workers)
        else:
            downloader(containertasks)


if __name__ == "__main__":
    asyncio.run(main())
