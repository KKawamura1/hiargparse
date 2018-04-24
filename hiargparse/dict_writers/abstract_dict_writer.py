from abc import ABC, abstractmethod
from typing import Union, Sequence, Any
from contextlib import contextmanager
from argparse import Action


class AbstractDictWriter(ABC):
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
            value: Union[str, Sequence[str]],
            commented: bool
    ) -> None:
        raise NotImplementedError

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
