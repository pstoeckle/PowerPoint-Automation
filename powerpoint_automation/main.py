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
from typing import Any, List, MutableMapping, Optional

from click import Context, Path, echo, group, option
from pptx import Presentation
from pptx.shapes.picture import Picture

from powerpoint_automation import __version__

LINUX_LIBREOFFICE = "/usr/bin/libreoffice"
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

_INPUT_DIRECTORY_OPTION = option(
    "--input-directory",
    "-d",
    type=Path(exists=True, file_okay=False, resolve_path=True),
    default=".",
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

    if (platform == "linux" or platform == "linux2") and isfile(LINUX_LIBREOFFICE):
        LIBRE_OFFICE = LINUX_LIBREOFFICE
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


@_INPUT_DIRECTORY_OPTION
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


@option("--inplace", "-i", is_flag=True, default=False)
@_INPUT_DIRECTORY_OPTION
@option("--hash-value", "-S", multiple=True, default=None)
@main_group.command()
def remove_picture(
    input_directory: str, hash_value: Optional[List[str]], inplace: bool
) -> None:
    """
    Remove the pictures from all slides.
    """
    if hash_value is None or len(hash_value) == 0:
        _LOGGER.info("No hashes ...")
        return
    hashes_set = frozenset(h.casefold() for h in hash_value)
    input_directory_path = pathlib_Path(input_directory)
    pptx_files = [
        f
        for f in input_directory_path.iterdir()
        if f.is_file() and f.suffix.casefold() == ".pptx" and not f.stem.startswith("~")
    ]
    for input_file in pptx_files:
        pres = Presentation(input_file)
        rewrite_file = False
        for slide in pres.slides:
            shapes_to_delete = []
            for shape in slide.shapes:
                if isinstance(shape, Picture):
                    if shape.image.sha1.casefold() in hashes_set:
                        shapes_to_delete.append(shape)
            if len(shapes_to_delete) > 0:
                rewrite_file = True
                for shape_to_delete in shapes_to_delete:
                    old_pic = shape_to_delete._element
                    old_pic.getparent().remove(old_pic)
        if rewrite_file:
            if inplace:
                _LOGGER.info(f"Rewrite file {input_file}")
                pres.save(input_file)
            else:
                new_file_name = (
                    str(input_file)
                    .replace(".pptx", ".out.pptx")
                    .replace(".PPTX", ".out.pptx")
                )
                _LOGGER.info(f"Write file {new_file_name}")
                pres.save(new_file_name)


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
