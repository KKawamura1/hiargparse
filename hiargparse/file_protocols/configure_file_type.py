import enum
from . import dict_readers, dict_writers


class ConfigureFileType(enum.Enum):
    """Write/Read supporting types"""

    toml = enum.auto()
    yaml = enum.auto()

    def get_reader(self) -> dict_readers.AbstractDictReader:
        if self is ConfigureFileType.toml:
            return dict_readers.TOMLReader()
        elif self is ConfigureFileType.yaml:
            return dict_readers.YAMLReader()
        else:
            raise ValueError('{} has no reader.'.format(self))

    def get_writer(self) -> dict_writers.AbstractDictWriter:
        if self is ConfigureFileType.toml:
            return dict_writers.TOMLWriter()
        elif self is ConfigureFileType.yaml:
            return dict_writers.YAMLWriter()
        else:
            raise ValueError('{} has no writer.'.format(self))
