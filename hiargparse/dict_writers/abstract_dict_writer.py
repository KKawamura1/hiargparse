from abc import ABC, abstractmethod
from typing import Union, Sequence, Any, List
from contextlib import contextmanager
from argparse import Action


class AbstractDictWriter(ABC):
    @abstractmethod
    def expand_help_text_from_action(self, action: Action) -> str:
        raise NotImplementedError()

    @abstractmethod
    def get_metavar_from_action(self, action: Action) -> str:
        raise NotImplementedError()

    @abstractmethod
    def begin_section(self, name: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def end_section(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def add_comment(
            self,
            comment: str
    ) -> None:
        raise NotImplementedError()

    @abstractmethod
    def add_value(
            self,
            name: str,
            values: Union[str, Sequence[str]],
            comment: str,
            comment_outs: bool
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def write_out(self) -> str:
        raise NotImplementedError()

    @contextmanager
    def make_section(self, name: str) -> Any:
        """call begin_section and ensure to call end_section later.

        usage:
            with writer.make_section('foo'):  # begin_section('foo') called
                ...
            # ensured to call end_section() here
        """
        self.begin_section(name)
        yield self
        self.end_section()

    def add_argument(
            self,
            action: Action,
            dest: str,
            comment_outs: bool
    ) -> None:
        help_text = self.expand_help_text_from_action(action)
        metavar = self.get_metavar_from_action(action)
        nargs = action.nargs
        values: Union[str, List[str]]
        if nargs is None or nargs == 1:
            values = metavar
        elif nargs == 0:
            values = []
        else:
            values = [metavar]
        self.add_value(name=dest, values=values, comment=help_text, comment_outs=comment_outs)
