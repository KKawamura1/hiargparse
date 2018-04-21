import argparse
from typing import Type, AbstractSet, TYPE_CHECKING
from typing_extensions import Protocol
from .exceptions import ArgumentError

# avoid cyclic importing
if TYPE_CHECKING:
    from .args_provider import ArgsProvider


class SupportsArgsProvider(Protocol):
    """Structural subtyping protocol which supports ArgsProvider."""

    @classmethod
    def get_args_provider(cls) -> 'ArgsProvider':
        ...


class ChildProvider:
    def __init__(
            self,
            cls: Type[SupportsArgsProvider],
            name: str = None,
            dest: str = None,
            prefix: str = None,
            no_provides: AbstractSet[str] = set()
    ) -> None:
        if name is None:
            name = cls.__name__  # type: ignore
            assert name is not None
        if dest is None:
            dest = name.replace('-', '_')
        if dest == '':
            raise ArgumentError('ChildProvider.dest must have '
                                'at least one character.')
        if prefix is None:
            prefix = name
        self.cls = cls
        self.name = name
        self.dest = dest
        self.prefix = prefix
        self.no_provides = set(no_provides)
