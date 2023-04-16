"""This module process of the comments to Issues objects"""
from __future__ import annotations
import logging
import sys
from functools import cached_property
from dataclasses import dataclass, field

sys.path.insert(0, ".")
from rnotes.parser import Tokens


__docformat__ = "google"


@dataclass
class Issue:
    """Data class of an issue (pull request's first comment)"""

    description: str
    ticket_number: int
    ticket_url: str
    ticket_title: str
    highlight: bool
    topic: str
    type: str
    image: str

    def from_comment(comment: dict[str, str]) -> Issue:
        """Convert a dictionary that represents the pull request's first comment.

        Args:
            comment (dict[str, str]): dictionary that represents the pull request's first comment.

        Returns:
            Issue: an Issue object.
        """
        return Issue(
            description=Issue.clean_text(comment[Tokens.DESCRIPTION]),
            ticket_number=comment[Tokens.TICKET_NUMBER],
            ticket_url=comment[Tokens.TICKET_URL],
            ticket_title=Issue.clean_text(comment[Tokens.TICKET_TITLE]),
            highlight=comment[Tokens.IS_HIGHLIGHT].lower() == "yes",
            topic=Issue.clean_text(comment[Tokens.TOPIC]),
            type=Issue.clean_text(comment[Tokens.TYPE]),
            image=comment[Tokens.IMAGE_MD],
        )

    @staticmethod
    def clean_text(string: str) -> str:
        """Clean the text from new lines"""
        return " ".join(string.replace("\n", " ").split())


@dataclass
class Topic:
    """Container of Issues (pull request's first comment) with a name and mapping between issue type to the relevant issues"""

    name: str
    "Name of the topic"
    type_to_issues: dict[str, list[Issue]] = field(default_factory=dict)
    "Mapping type to issues, for example: {'Bug': [Issue1, Issue2, ...], 'Enhancement': [Issue1, Issue2, ...], ...}"


class ReleaseData:
    """The proceed data with all the issues, topics, highlights, etc."""

    def __init__(self, issues: list[Issue], order_by_topics: list[str] = None, order_by_types: list[str] = None):
        """
        Args:
            issues (list[Issue]): list of Issues objects.
            order_by_topics (list[str], optional): topics names by object, that will be
                appeared in this order in the release notes. Defaults to None.
            order_by_types (list[str], optional): issues names by object, that will be
                appeared in this order in the release notes Defaults to None.
        """
        self._issues = issues
        self._order_by_topics = order_by_topics
        self._order_by_types = order_by_types

    @property
    def issues(self) -> list[Issue]:
        """
        Returns:
            list[Issue]: All the issues.
        """
        return self._issues

    @cached_property
    def highlights(self) -> list[Issue]:
        """
        Returns:
            list[Issue]: All the issues that marked as highlight.
        """
        issues = [issue for issue in self._issues if issue.highlight]
        logging.debug("%s highlights items found", len(issues))
        return sorted(issues, key=lambda issue: issue.ticket_number)

    @cached_property
    def topics(self) -> list[Topic]:
        """Constructs and returns all the topics.

        Returns:
            list[Topic]: List (ordered) of all the topics objects.
        """
        topic_names = sorted({issue.topic for issue in self._issues})
        if self._order_by_topics:
            topic_names = sorted(topic_names, key=lambda name: self._order_by_topics.index(name))
        topics: list[Topic] = []
        for topic_name in topic_names:
            topic = Topic(name=topic_name)
            issues = sorted(
                filter(
                    lambda issue: issue.topic == topic_name,
                    self._issues,
                ),
                key=lambda issue: issue.ticket_number,
            )
            if self._order_by_types:
                issues = sorted(issues, key=lambda issue: (self._order_by_types.index(issue.type), issue.ticket_number))
            for issue in issues:
                topic.type_to_issues.setdefault(issue.type, []).append(issue)
            topics.append(topic)
        logging.debug("%s topics found: %s", len(topic_names), ", ".join(map(lambda val: f"'{val}'", topic_names)))
        return topics

    @cached_property
    def issues_by_type(self, type_of_issue: str) -> list[Issue]:
        """
        Args:
            type_of_issue (str): type of the issue (for example, "Bug").

        Returns:
            list[Issue]: All the issues the marked with the given type_of_issue.
        """
        return [issue for issue in self._issues if issue.type == type_of_issue]
