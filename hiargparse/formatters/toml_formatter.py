from typing import Sequence, Union
from .write_formatter import WriteFormatter


class TOMLFormatter(WriteFormatter):
    def __init__(self, prog: str = 'hoge') -> None:
        super().__init__(prog)

    def _string_line_to_comment(self, string_line: str) -> str:
        return self._string_line_to_comment_with_comment_prefix(string_line, '#')

    def _assign_name_and_values(
            self,
            name: str,
            value: Union[Sequence[str], str]
    ) -> str:
        if isinstance(value, str):
            value_str = '\'{}\''.format(value)
        elif not value:
            value_str = '\'{}\''.format(self._supress_token)
        else:
            value_str = '[\'{}\']'.format(', '.join(value))
        return '{} = {}'.format(name, value_str)
