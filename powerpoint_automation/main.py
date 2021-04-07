"""
Convert.
"""
from logging import INFO, basicConfig, getLogger
from os.path import isfile
from pathlib import Path as pathlib_Path
from sys import platform, stdout
from typing import Any, List, Optional

from click import Context, Path, echo, group, option
from pptx import Presentation

from powerpoint_automation import __version__
from powerpoint_automation.logic.add_git_info import add_git_info_internal
from powerpoint_automation.logic.convert_presentations import (
    convert_presentations_internal,
)
from powerpoint_automation.logic.remove_picture import remove_picture_internal

LINUX_LIBREOFFICE = "/usr/bin/libreoffice"
MAC_OS_SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
LIBRE_OFFICE = "NOT_SET"

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
    convert_presentations_internal(
        input_directory_path, libre_office, output_directory_path
    )


@option("--old-year", "-O", type=int, default=2020)
@option("--new-year", "-N", type=int, default=2021)
@_INPUT_DIRECTORY_OPTION
@main_group.command()
def replace_date(input_directory: str, old_year: int, new_year: int) -> None:
    """
    Replace a date in the slides, e.g., 2020 -> 2021.
    """
    input_directory_path = pathlib_Path(input_directory)
    pptx_files = [
        f
        for f in input_directory_path.iterdir()
        if f.is_file() and f.suffix.casefold() == ".pptx" and not f.stem.startswith("~")
    ]
    for input_file in pptx_files:
        pres = Presentation(input_file)
        rewrite_file = False
        for slide_no, slide in enumerate(pres.slides):
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                old_text = shape.text.casefold().replace(" ", "")
                if (
                    "|securityengineering|" in old_text
                    and f"summer{old_year}" in old_text
                ):
                    shape.text = f"Prof. Dr. Alexander Pretschner (I4) | Security Engineering | Summer {new_year}"
                    rewrite_file = True
                    _LOGGER.info(f"{input_file}: Changing field on slide  {slide_no}")
                    continue
        if rewrite_file:
            pres.save(input_file)


@_INPUT_DIRECTORY_OPTION
@main_group.command()
def add_git_info(input_directory: str) -> None:
    """
    Adds a footer with the latest commit's hash and date.
    """
    input_directory_path = pathlib_Path(input_directory)
    add_git_info_internal(input_directory_path)


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
    remove_picture_internal(hashes_set, inplace, input_directory_path)


if __name__ == "__main__":
    main_group()
