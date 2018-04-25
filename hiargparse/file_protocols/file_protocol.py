from typing import Type
from typing_extensions import Protocol
from . import dict_readers, dict_writers


class FileProtocol(Protocol):
    @property
    def get_reader(self) -> Type[dict_readers.AbstractDictReader]:
        ...

    @property
    def get_writer(self) -> Type[dict_writers.AbstractDictWriter]:
        ...
