from typing_extensions import Protocol
from . import dict_readers, dict_writers


class FileProtocol(Protocol):
    def get_reader(self) -> dict_readers.AbstractDictReader:
        ...

    def get_writer(self) -> dict_writers.AbstractDictWriter:
        ...
