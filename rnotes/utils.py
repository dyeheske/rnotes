"""This module implements utilities functions for rnotes"""
from __future__ import annotations
import ast
import os
from pathlib import Path
import importlib.machinery
import importlib.abc
from types import ModuleType
from typing import Any, Union
import logging
import markdown
from rich.logging import RichHandler
from rich.console import Console


__docformat__ = "google"


class LogLevel:
    """Changing the log file under a context"""

    def __init__(self, log_level) -> None:
        """
        Args:
            log_level: the wanted log level.
        """
        self.log_level = log_level
        self.logger = logging.getLogger()
        self.handlers = self.logger.handlers if self.logger.handlers else ()
        self.current_level = self.logger.getEffectiveLevel()

    def __enter__(self):
        """Enter function - log level from now will be changed to the log level given in the __init__ method"""
        for handler in self.handlers:
            handler.setLevel(self.log_level)
        return self

    def __exit__(self, *args, **kwds):
        """Exit function - log level will be changed to the initial log level"""
        for handler in self.handlers:
            handler.setLevel(self.current_level)


def init_log(path: str = None, level: str = "NOTSET", jupyter: bool = False) -> None:
    """Initialize a `rich` log.

    Args:
        path (str, optional): Path of the log file. Defaults to None (stdout).
        level (str, optional): Level of the log file. Defaults to "NOTSET".
        jupyter (bool, optional): True if this log will be run in Jupyter Notebook. Defaults to False.
    """
    log_format = "%(message)s"
    logging.basicConfig(
        level=level or "NOTSET",
        format=log_format,
        handlers=[
            RichHandler(
                console=Console(
                    file=open(path, "w") if path else None,
                    force_jupyter=jupyter,
                    width=150
                )
            )
        ],
        force=True,
    )


def import_file(path: Path) -> ModuleType:
    """
    Alias for `exec_file` in module import mode.

    Args:
        path: path of file to import.

    Returns:
        A module object containing all of the identifiers defined in `path_to_file`,
        upon successful import.
    """
    return exec_file(path)


def eval_file(path: Path, identifiers: dict[str, Any] = None) -> ModuleType:
    """
    Alias for `exec_file` in module file evaluate mode.

    Args:
        path: path of file to import.
        identifiers: dictionary used for passing values into and back out of
            the execution of the code.

    Returns:
        Assuming the file contains a sequence of Python statement, and the
        final statement is an expression evaluation (including a function or
        method call), the result of that last evaluation, after all other
        statements in the file were executed, is returned.

        If the last statement is not an expression, then this function will
        behave like `exec_file`.
    """
    return exec_file(path, identifiers=identifiers or {}, evaluate=True)


def exec_file(
    path: Path,
    identifiers: dict[str, Any] = None,
    evaluate: bool = False,
) -> Union[bool, ModuleType]:
    """
    Execute code in a python file.

    Args:
        path: path of file to execute.
        identifiers: dictionary used for passing values into and back out of
            the execution of the code.
        evaluate: If `True` execute file as an expression and return the value
            of the expression

    Returns:
        When `identifiers` is specified:
            'True' if execution succeeded, or `False` otherwise.
        When `identifiers` not specified or is `None`:
            A module object containing all of the identifiers defined in `path_to_file`,
            upon successful import.

    Raises:
        When `identifiers` is not specified, any exception encountered when importing
        the module will be left uncaught.
    """
    path = path if path is None or isinstance(path, Path) else Path(path)
    if not path.exists():
        logging.error("Failed to import file '%s' which does not exist", path)
        return False

    if str(path.suffix).lower() != ".py":
        logging.error("Failed to import file '%s' which is not a python file", path)
        return False

    # Get package name from full path
    package_name = path.stem
    loader = importlib.machinery.SourceFileLoader(package_name, str(path))
    if identifiers is not None:
        identifiers["__file__"] = str(path)
        # Execute the module and affect the `identifiers` dictionary
        try:
            source = loader.get_source(package_name)
            if evaluate:
                stmts = list(ast.iter_child_nodes(ast.parse(source)))
                if not stmts:
                    return None
                [*exec_stmts, eval_stmt] = stmts
                if isinstance(eval_stmt, ast.Expr):
                    for stmt in exec_stmts:
                        exec(  # pylint: disable=exec-used
                            compile(ast.unparse(stmt), filename=path, mode="exec"),
                            identifiers,
                        )
                    return eval(  # pylint: disable=eval-used
                        compile(ast.unparse(eval_stmt), filename=path, mode="eval"),
                        identifiers,
                    )
                raise ImportError(f"Cannot evaluate code in '{path}', because the last statement is not an expression.")
            code = compile(source, path, mode="exec")
            exec(code, identifiers)  # pylint: disable=exec-used
            result = True
        except Exception as exc:
            logging.error("Failed to load the file '%s'", path)
            logging.error("Raised: %s", exc)
            raise
        logging.debug("successfully imported file '%s'", path)
        return result
    # Load the module
    result = ModuleType(package_name, f"Module loaded by exec_file('{path!s}')")
    loader.exec_module(result)
    return result


def get_file_name(tool_name: str, version_name: str, sfx: str = ".md") -> str:
    """Constructs and returns the file name of the release notes file.

    Args:
        tool_name (str): the name of the tool.
        version_name (str): the version name.
        sfx (str, optional): the suffix of the file. Defaults to ".md".

    Returns:
        str: the file name.
    """
    return f"release_notes_of-{'_'.join(tool_name.split()).lower()}-{'_'.join(version_name.replace('.', '_').split()).lower()}{sfx}"


def to_html(path: Path, suffix: str = "") -> Path:
    """Converts .md/.txt file to html file.

    Args:
        path (Path): path of the given file.
        suffix (str, optional): suffix to the html new file name. Defaults to "".

    Returns:
        Path: The path object of the new file.
    """
    html_file_path = None
    content = path.read_text()
    str_path = str(path.resolve())
    if path.suffix == ".md":
        html_content = markdown.markdown(content)
    else:
        html_content = '<html>\n<head>\n<title>' + str_path + '</title>\n</head>\n<body>\n<pre>\n'
        html_content += content.replace('<', '&lt;').replace('>', '&gt;')
        html_content += '\n</pre>\n</body>\n</html>'
    html_file_path = Path(os.path.splitext(str_path)[0] + f"{suffix}.html")
    html_file_path.write_text(html_content)
    return html_file_path
