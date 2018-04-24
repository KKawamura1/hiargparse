from argparse import HelpFormatter, SUPPRESS, Action
from typing import TypeVar, Generator, Any, no_type_check, Iterable, Sequence, List, Union
from pathlib import Path
from contextlib import contextmanager
import re
from ..configure_file_type import ConfigureFileType
from ..dict_writers import AbstractDictWriter, NullWriter


class WriteFormatter(HelpFormatter):
    """Formatter that make file-output.

    This class is highly based on argparse.HelpFormatter,
    which is the protected (not public) class except its name,
    so this class should be maintenanced carefully.
    """

    def __init__(
            self,
            prog: str,
            indent_increment: int = 0,
            max_help_position: int = 0,
            width: int = 80
    ) -> None:
        super().__init__(prog=prog, indent_increment=indent_increment,
                         max_help_position=max_help_position, width=width)
        self._re_white_spaces = re.compile(r'^ *')
        self._supress_token = '*SUPPRESS*'

    def _format_action(self, action: Action) -> str:
        option_strings: Sequence[str] = action.option_strings
        nargs: Union[int, str, None] = action.nargs
        current_indent: int = self._current_indent  # type: ignore
        # action dest (e.g. --help)
        if not option_strings:
            # positional arguments aren't written in the file
            return ''
        else:
            default_metavar: str = self._get_default_metavar_for_optional(action)  # type: ignore
            metavar: str = self._metavar_formatter(action, default_metavar)(1)[0]  # type: ignore
            # leftmost long (starts with --) name
            dest = option_strings[0]
            for option_string in option_strings:
                if option_string.startswith('--'):
                    dest = option_string
                    break
            values: Union[str, List[str]]
            if nargs is None or nargs == 1:
                values = metavar
            elif nargs == 0:
                values = []
            else:
                values = [metavar]
        assign_str = self._assign_name_and_values(dest, values)
        dest_line = '{}{}\n'.format(' ' * current_indent, assign_str)
        super_class_result: str = super()._format_action(action)  # type: ignore
        return_lines = super_class_result + dest_line + '\n'
        return self._string_lines_to_comments(return_lines)

    # protected methods used in this module
    # type-ignore is used to supress the type errors stand for their privateness
    def start_section(self, heading: str) -> None:
        super().start_section(heading)  # type: ignore

    def end_section(self) -> None:
        super().end_section()  # type: ignore

    def add_text(self, text: str) -> None:
        super().add_text(text)  # type: ignore

    def add_arguments(self, actions: Iterable[Action]) -> None:
        super().add_arguments(actions)  # type: ignore

    def format_help(self) -> str:
        return super().format_help()  # type: ignore

    # virtual methods
    def _assign_name_and_values(
            self,
            name: str,
            values: Union[Sequence[str], str]
    ) -> str:
        raise NotImplementedError()

    def _string_line_to_comment(
            self,
            string_line: str
    ) -> str:
        raise NotImplementedError()

    # useful methods for implement virtual methods
    def _string_line_to_comment_with_comment_prefix(
            self,
            string_line: str,
            comment_prefix: str
    ) -> str:
        if not string_line:
            return string_line
        assert '\n' not in string_line[:-1]
        match = self._re_white_spaces.search(string_line)
        assert match is not None
        end_pos = match.end()
        if end_pos == len(string_line):
            return string_line
        # like '    Foo = bar' to '    # Foo = bar'
        return '{}{} {}'.format(string_line[:end_pos], comment_prefix, string_line[end_pos:])

    # user methods
    def _string_lines_to_comments(
            self,
            document: str
    ) -> str:
        return '\n'.join([self._string_line_to_comment(line)
                          for line in document.split('\n')])
