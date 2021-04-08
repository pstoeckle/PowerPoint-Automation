"""
Convert PPTX to PDFs.
"""
from hashlib import sha3_256
from json import dump, load
from logging import getLogger
from pathlib import Path as pathlib_Path
from subprocess import call
from typing import MutableMapping

CACHE_FILE = ".powerpoint-automation.json"
_LOGGER = getLogger(__name__)


def convert_presentations_internal(
    input_directory_path: pathlib_Path,
    libre_office: str,
    output_directory_path: pathlib_Path,
) -> None:
    """

    :param input_directory_path:
    :param libre_office:
    :param output_directory_path:
    :return:
    """
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
