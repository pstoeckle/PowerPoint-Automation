# SPDX-FileCopyrightText: 2022 Patrick Stöckle.
# SPDX-License-Identifier: Apache-2.0
"""
Convert PPTX to PDFs.
"""
from hashlib import sha3_256
from json import dump, load
from logging import getLogger
from os import remove
from pathlib import Path
from subprocess import Popen, call
from sys import platform, stdout
from typing import AbstractSet, MutableMapping

from typer import echo

_CACHE_FILE = ".powerpoint-automation.json"
_LOGGER = getLogger(__name__)


def convert_presentations_internal(
    input_directory_path: Path,
    libre_office: Path,
    output_directory_path: Path,
    skip_files: AbstractSet[str],
) -> None:
    """

    :param skip_files:
    :param input_directory_path:
    :param libre_office:
    :param output_directory_path:
    :return:
    """
    _setup_output_directory(output_directory_path)
    cache_file = input_directory_path.joinpath(_CACHE_FILE)
    content = _load_cache(cache_file)
    files = list(input_directory_path.iterdir())
    files = [
        f
        for f in files
        if f.is_file() and f.suffix.casefold() == ".pptx" and not f.stem.startswith("~")
    ]
    for file in files:
        if file.stem.casefold().strip() in skip_files:
            echo(f"We will ignore {file}.")
            continue
        _convert_file(content, libre_office, file, output_directory_path)
    with cache_file.open("w") as f_write:
        _LOGGER.debug(f"Write cache back to {cache_file}.")
        dump(content, f_write, indent=4)


def _convert_file(
    cache_content: MutableMapping[str, str],
    libre_office: Path,
    file: Path,
    output_directory_path: Path,
) -> None:
    file_hash = hash_file(file)
    if str(file) in cache_content.keys() and cache_content[str(file)] == file_hash:
        echo(f"The file {file} has not changed since the last conversion.")
        return
    echo(f"Convert {file} to PDF")
    if platform == "win32":
        echo("Converting on Windows")
        script_path = output_directory_path.joinpath("t.ps1")
        out_file = output_directory_path.joinpath(
            file.name.replace(file.suffix, ".pdf")
        )
        with script_path.open("w") as f_write:
            f_write.write(
                rf"""
$ppt = New-Object -com powerpoint.application
$open_presentation = $ppt.Presentations.Open("{file}")
$open_presentation.SaveAs("{out_file}", [Microsoft.Office.Interop.PowerPoint.PpSaveAsFileType]::ppSaveAsPDF)
$open_presentation.Close()
"""
            )
        _LOGGER.info(f"Opening PowerPoint ...")
        p = Popen(["powershell.exe", '"' + str(script_path) + '"'], stdout=stdout)
        p.communicate()
        _LOGGER.info(f"Closing PowerPoint ...")
        remove(script_path)
    else:
        call(
            [
                str(libre_office),
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


def _load_cache(cache_file: Path) -> MutableMapping[str, str]:
    content: MutableMapping[str, str]
    if cache_file.is_file():
        with cache_file.open() as f_read:
            content = load(f_read)
    else:
        content = {}
    return content


def _setup_output_directory(output_directory_path: Path) -> None:
    if not output_directory_path.is_dir():
        output_directory_path.mkdir()


def hash_file(file: Path) -> str:
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
