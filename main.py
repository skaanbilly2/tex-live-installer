import argparse, argcomplete
from doctest import OutputChecker
import logging
import asyncio
import random
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from tex_live_installer.helpers.reader import get_containers
from tex_live_installer.helpers.extract import extract_file
from tex_live_installer.downloaders.async_pooled_all import downloader_async
from tex_live_installer.downloaders.seq_pooled import downloader

from config import (
    OUTPUT_FOLDER,
    TEXLIVE_TLPDB,
    PACKAGES_JSON_FILE,
    MIRROR_BASE_URL,
    N_packages,
)


async def main():
    parser = argparse.ArgumentParser("Installer")
    parser.add_argument("command", type=str, choices=("extract_tlpdb", "install"))
    parser.add_argument("--inputfile", type=str, help="input file", default=None)
    parser.add_argument(
        "--outputfile",
        type=str,
        help="outputfile in case of extract command",
        default=PACKAGES_JSON_FILE,
    )
    parser.add_argument(
        "--n_packages",
        type=int,
        help="Limits the number of installed packages to the first N",
        default=N_packages,
    )
    parser.add_argument(
        "--asyncio", type=str, choices=("True", "False"), default="False"
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
        if args.inputfile is None:
            args.inputfile = TEXLIVE_TLPDB
        extract_file(
            infile=pathlib.Path(args.inputfile), outfile=pathlib.Path(args.outputfile)
        )
    elif args.command == "install":
        if args.inputfile is None:
            args.inputfile = PACKAGES_JSON_FILE
        containertasks = get_containers(
            filepath=pathlib.Path(args.inputfile),
            mirror_url=MIRROR_BASE_URL,
            output_folder=pathlib.Path(OUTPUT_FOLDER),
        )
        random.shuffle(containertasks)
        containertasks = containertasks[: min(len(containertasks), args.n_packages)]
        if args.asyncio == "True":
            await downloader_async(containertasks, max_parrallel_req=args.n_workers)
        else:
            downloader(containertasks)


if __name__ == "__main__":
    asyncio.run(main())
