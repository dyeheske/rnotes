"""This module implements the query of the data from GitHub"""
import logging
import os
from pathlib import Path
import sys
from functools import cached_property
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from tempfile import mkdtemp
from github import Github, UnknownObjectException
from github.PullRequest import PullRequest
from github.Tag import Tag
from github.Repository import Repository

sys.path.insert(0, ".")
from rnotes.utils import LogLevel


__docformat__ = "google"


@dataclass
class GithubPullRequest:
    """Pull request object to store the basic information of the pull request"""

    name: str
    url: str
    author: str
    comment: str


class GithubRepository:
    """Wrapper to the github.repository class"""

    def __init__(self, repository: Repository) -> None:
        """
        Args:
            repository (Repository): github.Repository instance.
        """
        self._repository = repository
        self._tmp_dir = Path(mkdtemp())

    @property
    def repository(self) -> Repository:
        """
        Returns:
            Repository: the github.Repository instance.
        """
        return self._repository

    @cached_property
    def tags(self) -> dict[str, Tag]:
        """
        Returns:
            dict[str, Tag]: All the tags in the repository, as mapping from the tag name to the github.Tag object.
        """
        with LogLevel(logging.INFO if "DEBUG" not in os.environ else logging.DEBUG):
            return {tag.name: tag for tag in self._repository.get_tags()}

    def get_tag(self, tag_name: str) -> Optional[Tag]:
        """Get the github.Tag object based on the given tag name.

        Args:
            tag_name (str): the name of the tag.

        Returns:
            Optional[Tag]: Tag object, if the tag found, else None.
        """
        logging.info("Fetching the tag: '%s'", tag_name)
        if tag := self.tags.get(tag_name):
            return tag
        assert tag, f"No such tag: '{tag_name}'"

    def download_file(self, relative_path: str) -> Optional[Path]:
        """Download a single file to the temp path as defined in __init__, and returns the new path.

        Args:
            relative_path (str): path of the file, relative to the top of the repository.

        Returns:
            Optional[Path]: Path object of the downloaded file if found, else None.
        """
        with LogLevel(logging.INFO if "DEBUG" not in os.environ else logging.DEBUG):
            new_path = self._tmp_dir / Path(relative_path).name
            try:
                downloaded_file = self._repository.get_contents(relative_path)
            except UnknownObjectException:
                logging.warning("Didn't find the path for: <top of the repository>/%s", relative_path)
                return None
            with open(new_path, "wb") as file:
                file.write(downloaded_file.decoded_content)
            return new_path

    def get_pull_requests_between_dates(self, from_date: datetime, to_date: datetime = None) -> set[PullRequest]:
        """Get all the pull requested that merged between the given 2 dates.

        Args:
            from_date (datetime): date to start the query.
            to_date (datetime, optional): date to end the query. Defaults to Now.

        Returns:
            set[PullRequest]: Set of all the github.PullRequest objects between the given 2 dates.
        """
        logging.info(
            "Fetching all the pull requests between: ['%s' < PR merged time <= '%s']", from_date, to_date if to_date else "Now"
        )
        to_date = to_date or datetime.max
        relevant_pulls = set()
        all_pulls = self._repository.get_pulls(state="closed", sort="merged", direction="desc")
        for pr in all_pulls:
            if pr.merged_at is None:
                continue
            if from_date < pr.merged_at <= to_date:
                relevant_pulls.add(pr)
            if pr.merged_at < from_date:
                break
        logging.info("Found %s pull requests", len(relevant_pulls))
        return relevant_pulls

    def get_pull_requests(self, from_tag_name: str, to_tag_name: str = None) -> list[GithubPullRequest]:
        """Get all the pull requested that merged between the given 2 tags, based on the time that the pull requested merged,
        and the time that the commit of each tag created.

        Args:
            from_tag_name (str): tag to start the query.
            to_tag_name (str, optional): tag to end the query. Defaults to None (all the commits from the `from_tag`).

        Returns:
            list[GithubPullRequest]: List of all the pull requests (GithubPullRequest object) between the 2 tags.
        """
        with LogLevel(logging.INFO if "DEBUG" not in os.environ else logging.DEBUG):
            from_date = self.get_tag(tag_name=from_tag_name).commit.commit.author.date
            to_date = self.get_tag(tag_name=to_tag_name).commit.commit.author.date if to_tag_name else None
            pull_requests = self.get_pull_requests_between_dates(from_date=from_date, to_date=to_date)
            return [
                GithubPullRequest(
                    name=pull_request.title,
                    url=pull_request.html_url,
                    author=pull_request.user.login,
                    comment=pull_request.body,
                )
                for pull_request in sorted(pull_requests, key=lambda pr: pr.merged_at)
            ]

    def get_pull_requests_by_commit(self, commit_sha_from: str, commit_sha_to: str) -> list[GithubPullRequest]:
        """Get all the pull requested that merged between the given 2 commits sha, based on the time that the pull requested merged,
        and the time that the commit of each tag created.

        Args:
            from_tag_name (str): tag to start the query.
            to_tag_name (str, optional): tag to end the query. Defaults to None (all the commits from the `from_tag`).

        Returns:
            list[GithubPullRequest]: List of all the pull requests (GithubPullRequest object) between the 2 tags.
        """
        with LogLevel(logging.INFO if "DEBUG" not in os.environ else logging.DEBUG):
            from_date = self._repository.get_commit(sha=commit_sha_from).commit.author.date
            to_date = self._repository.get_commit(sha=commit_sha_to).commit.author.date
            pull_requests = self.get_pull_requests_between_dates(from_date=from_date, to_date=to_date)
            return [
                GithubPullRequest(
                    name=pull_request.title,
                    url=pull_request.html_url,
                    author=pull_request.user.login,
                    comment=pull_request.body,
                )
                for pull_request in sorted(pull_requests, key=lambda pr: pr.merged_at)
            ]


def get_repository(github: Github, repository_name: str) -> Optional[Repository]:
    """Get the github.Repository instance, based on the given repository_name and the GitHub instance.

    Args:
        github (Github): GitHub instance.
        repository_name (str): the name of the repository.

    Returns:
        Optional[Repository]: the repository object if there is such, else None
    """
    try:
        return github.get_repo(repository_name)
    except UnknownObjectException:
        logging.fatal("The repository: '%s' does not exist", repository_name)
        return None


def get_github_repository(repository_name: str, token: str = None) -> GithubRepository:
    """Get the GithubRepository instance, based on the given repository_name and the token.

    Args:
        repository_name (str): the name of the repository.
        token (str, optional): GitHub personal token. Defaults: environment variable: GITHUB_TOKEN.

    Returns:
        GithubRepository: instance of the GithubRepository.
    """
    token = token or os.environ.get("GITHUB_TOKEN")
    token_doc_path = "https://docs.github.com/en/enterprise-server@3.4/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
    assert token is not None, (
        "Token argument is `None`, but the GITHUB_TOKEN environment variable didn't set. "
        f"To set a personal token: {token_doc_path}, then "
        "copy the token (for example: 'gda_XoNP26Vtafm') and either pass it as an argument to this function "
        "or set the token value to the following environment variable: GITHUB_TOKEN"
    )
    with LogLevel(logging.INFO if "DEBUG" not in os.environ else logging.DEBUG):
        logging.info("Fetching the repository: '%s'", repository_name)
        repository = get_repository(github=Github(token), repository_name=repository_name)
        assert repository, f"Failed to get the repository: '{repository_name}'"
        return GithubRepository(repository=repository)
