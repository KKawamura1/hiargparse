import enum
from . import dict_readers, dict_writers
from typing import Type


class ConfigureFileType(enum.Enum):
    toml = enum.auto()
    yaml = enum.auto()

    @property
    def get_reader(self) -> Type[dict_readers.AbstractDictReader]:
        if self is ConfigureFileType.toml:
            return dict_readers.TOMLReader
        elif self is ConfigureFileType.yaml:
            return dict_readers.YAMLReader
        else:
            raise ValueError('{} has no reader.'.format(self))

    @property
    def get_writer(self) -> Type[dict_writers.AbstractDictWriter]:
        if self is ConfigureFileType.toml:
            return dict_writers.TOMLWriter
        elif self is ConfigureFileType.yaml:
            return dict_writers.YAMLWriter
        else:
            raise ValueError('{} has no writer.'.format(self))
