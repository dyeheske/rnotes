"""This module implements the full flow of rnotes"""
from __future__ import annotations
import logging
import os
import sys
from pathlib import Path
import tempfile
from rich import pretty, traceback
import fire

sys.path.insert(0, ".")
from rnotes.utils import eval_file, import_file, init_log, get_file_name, to_html
from rnotes.query import GithubPullRequest, GithubRepository, get_github_repository
from rnotes.parser import CommentParser, load_grammar
from rnotes.process import ReleaseData, Issue
from rnotes.writer import ReleaseNotesWriter, load_template


__docformat__ = "google"


def generate_release_notes(
    repository_name: str,
    from_tag: str,
    to_tag: str,
    version_name: str = None,
    output_dir: str | Path = None,
    file_name: str | Path = None,
    grammar_path: str | Path = None,
    release_notes_path: str | Path = None,
    additional_content_path: str | Path = None,
    token: str = None,
    html: bool = True,
) -> None:
    """Create a release notes for the given repository.

    Args:
        repository_name (str): Name of the repository.
        from_tag (str): Tag name we want the release notes from.
        to_tag (str): Tag name we want the release notes until.
        version_name (str, optional): overwrite the version name that will be appeared in the release notes.
            Defaults to `to_tag` argument..
        output_dir (str | Path, optional): Directory that we want our release notes file to be dumped.
            Defaults to tmp directory.
        file_name (str | Path, optional): Overwrite the file name of the release notes.
            Defaults to concatenation of the tool name and the version name.
        grammar_path (str | Path, optional): Grammar file (.py).
            Defaults to the file in ".rnotes" of the given repository.
        release_notes_path (str | Path, optional): Release notes template file (.j2).
            Defaults to the file in ".rnotes" of the given repository.
        additional_content_path (str | Path, optional): Additional content file (.py)
            Defaults to the file in ".rnotes" of the given repository.
        token (str, optional): GitHub personal token. Defaults: environment variable: GITHUB_TOKEN
        html (bool, optional): If True, generates html file of the release notes.
    """
    grammar_path = grammar_path or os.environ.get("RNOTES_GRAMMAR_PATH")
    release_notes_path = release_notes_path or os.environ.get("RNOTES_RELEASE_NOTES_PATH")
    additional_content_path = additional_content_path or os.environ.get("RNOTES_ADDITIONAL_CONTENT_PATH")
    # Query the GitHub's repository and all comments between the 2 tags:
    repository: GithubRepository = get_github_repository(repository_name=repository_name, token=token)
    pull_requests: list[GithubPullRequest] = repository.get_pull_requests(from_tag, to_tag)
    # Parse all the comments:
    grammar_path = grammar_path or repository.download_file(".rnotes/grammar.py")
    grammar = load_grammar(path=grammar_path)
    parser = CommentParser(grammar=grammar)
    all_comments = parser.parse_pull_requests(pull_requests=pull_requests)
    # Process all the comments:
    issues: list[Issue] = [Issue.from_comment(comment) for comment in all_comments]
    grammar_module = import_file(grammar_path)
    release_data = ReleaseData(
        issues=issues,
        order_by_topics=grammar_module.all_topics if "all_topics" in grammar_module.__dict__ else None,
        order_by_types=grammar_module.all_types if "all_types" in grammar_module.__dict__ else None,
    )
    # Add additional content:
    additional_content = {}
    additional_content_path = additional_content_path or Path(repository.download_file(".rnotes/additional_content.py"))
    if additional_content_path:
        logging.info("Loading the additional content file from: %s", Path(additional_content_path).resolve())
        additional_content = eval_file(additional_content_path)
        assert isinstance(additional_content, dict), f"Failed to eval the file: {additional_content_path} (expected dict)"
    version_name = version_name or to_tag
    tool_name = additional_content.get("tool_name") or repository_name.split("/")[1]
    additional_content["tool_name"] = tool_name
    additional_content["version_name"] = version_name
    # Dump release notes:
    file_name = file_name or get_file_name(tool_name, version_name)
    release_notes_path = release_notes_path or repository.download_file(".rnotes/release_notes.j2")
    template = load_template(path=release_notes_path)
    writer = ReleaseNotesWriter(template=template)
    output_dir = output_dir or tempfile.mkdtemp()
    writer.write(
        output_dir=output_dir,
        file_name=file_name,
        release_data=release_data,
        additional_content=additional_content,
    )
    path = (Path(output_dir) / file_name).resolve()
    logging.info("Release notes path: %s", path.resolve())
    if not html:
        return
    html_path = to_html(path)
    logging.info("Release notes path (HTML): %s", html_path.resolve())


if __name__ == "__main__":
    pretty.install()
    traceback.install(show_locals=False, width=1000, extra_lines=7)
    init_log(level="INFO")
    fire.Fire(
        dict(
            generate=generate_release_notes,
        )
    )
