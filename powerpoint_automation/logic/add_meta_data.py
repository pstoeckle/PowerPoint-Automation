"""
Add the meta data to the PPTX.
"""
from datetime import datetime
from logging import getLogger
from os import linesep
from pathlib import Path
from subprocess import check_output
from typing import Sequence

from pptx import Presentation

_LOGGER = getLogger(__name__)


def add_meta_data_internal(author: Sequence[str], input_directory_path: Path) -> None:
    """

    :param author:
    :param input_directory_path:
    :return:
    """
    pptx_files = [
        f
        for f in input_directory_path.iterdir()
        if f.is_file() and f.suffix.casefold() == ".pptx" and not f.stem.startswith("~")
    ]
    for input_file in pptx_files:
        _LOGGER.info(f"Processing file {input_file}")
        pres = Presentation(input_file)
        commit_date = check_output(
            ["git", "log", "-n", "1", "--pretty=format:%aI", "--", input_file]
        ).decode("utf8")
        last_commit = check_output(
            ["git", "log", "-n", "1", "--pretty=format:%h", "--", input_file]
        ).decode("utf8")
        commits = check_output(
            ["git", "log", "--follow", "--pretty=format:%aI", "--", input_file]
        ).decode("utf8")
        *_, first_commit_date = commits.split(linesep)
        try:
            pres.core_properties.created = datetime.fromisoformat(first_commit_date)
        except ValueError:
            _LOGGER.warning(f"We could not determine creation date for {input_file}")

        try:
            pres.core_properties.modified = datetime.fromisoformat(commit_date)
        except ValueError:
            _LOGGER.warning(f"We could not last change date for {input_file}")
        pres.core_properties.version = last_commit
        pres.core_properties.author = ", ".join(author)
        pres.core_properties.language = "English"
        pres.core_properties.keywords = "Security"
        pres.core_properties.category = "Lecture slides"
        pres.core_properties.content_status = "final"
        pres.save(input_file)
        _LOGGER.info(f"{input_file}: Done")
