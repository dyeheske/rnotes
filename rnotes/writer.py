"""This module implements the writer of the release notes"""
from __future__ import annotations
import sys
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, ".")
from rnotes.process import ReleaseData


__docformat__ = "google"


class ReleaseNotesWriter:
    """The writer of all the issues and additional content, based on the given template"""

    def __init__(self, template) -> None:
        """
        Args:
            The template object.
        """
        self._template = template

    @property
    def template(self):
        """
        Returns:
            The template object.
        """
        return self._template

    def write(
        self,
        output_dir: str | Path,
        file_name: str | Path,
        release_data: ReleaseData,
        additional_content: dict[str, str],
    ) -> None:
        """Write the release notes file.

        Args:
            output_dir (str | Path): Directory that we want our release notes file to be dumped.
            file_name (str | Path): File name of the release notes file.
            release_data (ReleaseData): The ReleaseData object (contains all the Issues).
            additional_content (dict[str, str]): Additional content to be written.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        file_path = output_dir / file_name
        release_data_content = dict(
            topics=release_data.topics,
            highlights=release_data.highlights,
            type_to_issue=release_data.type_to_issue,
            len=len,
        )
        logging.debug("Rendering the Jinja Template with the content")
        output = self._template.render(**(release_data_content | additional_content))
        logging.debug("Writing release notes to: %s", file_path.resolve())
        file_path.write_text(output)


def load_template(path: str | Path):
    """Load the template file (.j2).

    Args:
        path (str | Path): Path to the release notes template file (Jinja).

    Returns:
        The template object.
    """
    path = path if path is None or isinstance(path, Path) else Path(path)
    assert path.exists(), f"No such file: {path.resolve()}"
    logging.info("Loading the release notes template file from: %s", path.resolve())
    file_loader = FileSystemLoader(str(path.parent.resolve()))
    env = Environment(loader=file_loader)
    template = env.get_template(path.name)
    return template
