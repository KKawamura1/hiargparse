from .abstract_dict_writer import AbstractDictWriter
from typing import List, Union, Sequence
from argparse import Action


class NullWriter(AbstractDictWriter):
    def __init__(
            self
    ) -> None:
        pass

    def expand_help_text_from_action(self, action: Action) -> str:
        return ''

    def get_metavar_from_action(self, action: Action) -> List[str]:
        return ['']

    def begin_section(self, name: str) -> None:
        pass

    def end_section(self) -> None:
        pass

    def add_comment(
            self,
            comment: str
    ) -> None:
        pass

    def add_value(
            self,
            name: str,
            values: Union[str, Sequence[str]],
            comment: str,
            comment_outs: bool
    ) -> None:
        pass

    def write_out(self) -> str:
        return ''
