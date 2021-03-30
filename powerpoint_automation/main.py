"""
Convert.
"""
from hashlib import sha3_256
from json import dump, load
from logging import INFO, basicConfig, getLogger
from os.path import isfile
from pathlib import Path as pathlib_Path
from subprocess import call
from sys import platform, stdout
from typing import Any, MutableMapping

from click import Context, Path, echo, group, option

from powerpoint_automation import __version__

MAC_OS_SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

LIBRE_OFFICE = "NOT_SET"
CACHE_FILE = ".powerpoint-automation.json"

_LOGGER = getLogger(__name__)
basicConfig(
    format="%(levelname)s: %(asctime)s: %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=INFO,
    stream=stdout,
)


def _print_version(ctx: Context, _: Any, value: Any) -> None:
    """

    :param ctx:
    :param _:
    :param value:
    :return:
    """
    if not value or ctx.resilient_parsing:
        return
    echo(__version__)
    ctx.exit()


def _set_libreoffice() -> None:
    global LIBRE_OFFICE

    if (platform == "linux" or platform == "linux2") and isfile("/usr/bin/libreoffice"):
        LIBRE_OFFICE = "/usr/bin/libreoffice"
    elif platform == "darwin" and isfile(MAC_OS_SOFFICE):
        LIBRE_OFFICE = MAC_OS_SOFFICE
    else:
        _LOGGER.critical(f"Could not find Libreoffice... ({platform}")


_set_libreoffice()


@group()
@option(
    "--version",
    is_flag=True,
    callback=_print_version,
    expose_value=False,
    is_eager=True,
    help="Version",
)
def main_group() -> None:
    """

    :return:
    """


@option(
    "--input-directory",
    "-d",
    type=Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
)
@option(
    "--output-directory",
    "-o",
    type=Path(file_okay=False, resolve_path=True),
    default="dist",
)
@option(
    "--libre-office",
    "-L",
    type=Path(exists=True, resolve_path=True, dir_okay=False),
    default=LIBRE_OFFICE,
)
@main_group.command()
def convert_presentations(
    input_directory: str, output_directory: str, libre_office: str
) -> None:
    """
    Converts PowerPoint files to PDFs.
    """
    input_directory_path = pathlib_Path(input_directory)
    output_directory_path = pathlib_Path(output_directory)
    _setup_output_directory(output_directory_path)
    cache_file = input_directory_path.joinpath(CACHE_FILE)
    content = _load_cache(cache_file)
    files = list(input_directory_path.iterdir())
    files = [
        f
        for f in files
        if f.is_file() and f.suffix.casefold() == ".pptx" and not f.stem.startswith("~")
    ]
    for file in files:
        _convert_file(content, libre_office, file, output_directory_path)
    with cache_file.open("w") as f_write:
        dump(content, f_write, indent=4)


def _convert_file(
    cache_content: MutableMapping[str, str],
    libre_office: str,
    file: pathlib_Path,
    output_directory_path: pathlib_Path,
) -> None:
    file_hash = hash_file(file)
    if str(file) in cache_content.keys() and cache_content[str(file)] == file_hash:
        _LOGGER.info(f"The file {file} has not changed since the last conversion.")
        return
    _LOGGER.info(f"Convert {file} to PDF")
    call(
        [
            libre_office,
            "--headless",
            "--convert-to",
            "pdf",
            file,
            "--print-to-file",
            "--outdir",
            str(output_directory_path),
        ]
    )
    cache_content[str(file)] = file_hash


def _load_cache(cache_file: pathlib_Path) -> MutableMapping[str, str]:
    content: MutableMapping[str, str]
    if cache_file.is_file():
        with cache_file.open() as f_read:
            content = load(f_read)
    else:
        content = {}
    return content


def _setup_output_directory(output_directory_path: pathlib_Path) -> None:
    if not output_directory_path.is_dir():
        output_directory_path.mkdir()


def hash_file(file: pathlib_Path) -> str:
    """
    Tp.
    """
    if not file.is_file():
        return ""
    current_sha = sha3_256()
    with file.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            current_sha.update(chunk)
    return current_sha.hexdigest()


if __name__ == "__main__":
    main_group()
