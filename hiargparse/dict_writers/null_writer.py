from .abstract_dict_writer import AbstractDictWriter
from argparse import Action


class NullWriter(AbstractDictWriter):
    def begin_group(self, name: str) -> None:
        pass

    def end_group(self) -> None:
        pass

    def add_arg(
            self,
            action: Action,
            dest: str
    ) -> None:
        pass
