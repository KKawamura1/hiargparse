from abc import ABC, abstractmethod
from typing import Generator, TypeVar
from contextlib import contextmanager
from argparse import Action


T = TypeVar('T', bound='AbstractDictWriter')


class AbstractDictWriter(ABC):
    @abstractmethod
    def begin_group(self, name: str) -> None:
        raise NotImplementedError()

    @abstractmethod
    def end_group(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def add_arg(
            self,
            action: Action,
            dest: str
    ) -> None:
        raise NotImplementedError()

    @contextmanager
    def make_group(self: T, name: str) -> Generator[T, None, None]:
        """call begin_group and ensure to call end_group later.

        usage:
            with writer.make_group('foo'):  # begin_group('foo') called
                ...
            # ensured to call end_group() here
        """
        self.begin_group(name)
        yield self
        self.end_group()
