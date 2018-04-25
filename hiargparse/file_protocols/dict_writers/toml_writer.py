from .abstract_dict_writer import AbstractDictWriter
from typing import Union, Sequence, List


class TOMLWriter(AbstractDictWriter):
    def __init__(
            self,
            indent_size: int = 2
    ) -> None:
        self._indent_size = indent_size
        self._texts = ''
        self._indent_level = 0
        self._section_names: List[str] = list()

        self._begin_root_section()

    def _begin_root_section(self) -> None:
        pass

    def _end_root_section(self) -> None:
        pass

    def begin_section(self, name: str) -> None:
        self._section_names.append(name)
        self._add_line('[{}]'.format('.'.join(self._section_names)))
        self._indent()

    def end_section(self) -> None:
        self._dedent()
        self._section_names.pop()

    def add_comment(
            self,
            comment: str
    ) -> None:
        self._add_line('## {}'.format(comment))
        self._add_line()

    def add_value(
            self,
            name: str,
            values: Union[str, Sequence[str]],
            comment: str,
            comment_outs: bool
    ) -> None:
        self._add_line('## {}'.format(comment))
        if comment_outs:
            self._add_line('# {} = {}'.format(name, values))
        else:
            self._add_line('{} = {}'.format(name, values))
        self._add_line()

    def write_out(self) -> str:
        self._end_root_section()
        return self._texts

    def _indent(self) -> None:
        self._indent_level += 1

    def _dedent(self) -> None:
        self._indent_level -= 1

    def _line_header(self) -> str:
        return ' ' * (self._indent_level * self._indent_size)

    def _add_line(self, line: str = None) -> None:
        if line is None:
            new_line = '\n'
        else:
            new_line = '{}{}\n'.format(self._line_header(), line)
        self._texts += new_line
