"""This module implements the parser of pull requests comments"""
from __future__ import annotations
from pathlib import Path
from parsimonious import ParseError
from rich.logging import logging
from functools import cached_property
from enum import Enum
from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor
import sys

sys.path.insert(0, ".")
from rnotes.utils import eval_file
from rnotes.query import GithubPullRequest


__docformat__ = "google"


class Tokens(str, Enum):
    """Pre define tokens for the parser"""

    TICKET_NUMBER = "ticket_number"
    TICKET_URL = "ticket_url"
    TICKET_TITLE = "ticket_title"
    TYPE = "type"
    TOPIC = "topic"
    IS_HIGHLIGHT = "is_highlight"
    INCLUDE = "include"
    DESCRIPTION = "description"
    IMAGE_MD = "image_md"


class CommentParser:
    """The parser for the pull requests comment"""

    class SyntaxTreeBuilder(NodeVisitor):
        """Overwrite the behavior of the default parser tree"""

        @cached_property
        def leaf_name_to_value(self) -> dict[str, str]:
            """
            Returns:
                dict[str, str]: Mapping between the pre defined tokens to their values.
            """
            return {token.value: None for token in Tokens}

        def generic_visit(self, node, visited_children):
            """Overwrite the generic_visit, by storing the relevant data in the leaf_name_to_value dict.

            Args:
                node: node in the parser tree.
                visited_children: children of the node in the parser tree.

            Returns:
                the current nodes (same as in the default generic_visit method).
            """
            if node and node.expr_name in self.leaf_name_to_value:
                self.leaf_name_to_value[node.expr_name] = node.text
            return visited_children or node

    def __init__(self, grammar: Grammar) -> None:
        """
        Args:
            grammar (Grammar): the grammar object.
        """
        self._grammar = grammar

    @property
    def grammar(self):
        """
        Returns:
            the grammar object
        """
        return self._grammar

    def parse_comment(self, comment_text: str) -> dict[str, str]:
        """Parsing a single comment.

        Args:
            comment_text (str): the text of the comment.

        Returns:
            dict[str, str]: Mapping between the pre define token to the value as appears in the comment text.
        """
        tree = self._grammar.parse(comment_text)
        builder = CommentParser.SyntaxTreeBuilder()
        builder.visit(tree)
        comment = builder.leaf_name_to_value
        return comment

    def parse_pull_requests(self, pull_requests: list[GithubPullRequest]) -> list[dict[str, str]]:
        """Parse all the given pull requests.

        Args:
            pull_requests (list[GithubPullRequest]): List of GithubPullRequest objects.

        Returns:
            list[dict[str, str]]: All the comments after parsing (list of the results as defined in the method: `parse_comment`)
        """
        all_comments: list[dict[str, str]] = []
        for pull_request in pull_requests:
            try:
                if not pull_request.comment:
                    logging.error(
                        "Ignored the pull request: '%s' (url: '%s'), \nreason: first comment is empty",
                        pull_request.name,
                        pull_request.url,
                    )
                    continue
                comment_text = " ".join(pull_request.comment.split())
                logging.info("Parsing PR: '%s' (url: '%s')", pull_request.name, pull_request.url)
                comment = self.parse_comment(comment_text=comment_text)
                if comment.get(Tokens.INCLUDE, "").lower() == "no":
                    logging.info("Ignored (as expected) the pull request: '%s' (url: '%s')", pull_request.name, pull_request.url)
                    continue
                all_comments.append(comment)
            except ParseError as error:
                logging.error(
                    "Failed to parse the pull request: '%s' (url: '%s'), \nreason: %s: \"%s\"",
                    pull_request.name,
                    pull_request.url,
                    type(error).__name__,
                    str(error).replace("\n", ""),
                )
        return all_comments


def loads_grammar(text: str) -> Grammar:
    """Load the given grammar text.

    Args:
        text (str): The text of the grammar.

    Returns:
        Grammar: the Grammar object.
    """
    return Grammar(text)


def load_grammar(path: str | Path) -> Grammar:
    """Load the given grammar file.

    Args:
        path (str | Path): Path to the grammar (.py) file.

    Returns:
        Grammar: the Grammar object.
    """
    path = path if path is None or isinstance(path, Path) else Path(path)
    assert path.exists(), f"No such file: {path.resolve()}"
    grammar_str = eval_file(path)
    assert isinstance(grammar_str, str), f"File: {path.resolve()} must ends with a python string " "that represents the grammar"
    logging.info("Loading the grammar file from: %s", path.resolve())
    return loads_grammar(grammar_str)
