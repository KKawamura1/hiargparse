from .abstract_dict_writer import AbstractDictWriter
from typing import Union, Sequence


class NullWriter(AbstractDictWriter):
    def __init__(
            self
    ) -> None:
        pass

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
