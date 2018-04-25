import enum


class OriginType(enum.Enum):
    DefaultValue = enum.auto()
    SetFromArg = enum.auto()
    Unknown = enum.auto()
