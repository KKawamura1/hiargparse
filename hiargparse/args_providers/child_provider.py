from typing import Type, AbstractSet, TYPE_CHECKING
from typing_extensions import Protocol
from hiargparse.miscs import if_none_then
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
    """Struct that represents a child ArgsProvider."""

    def __init__(
            self,
            cls: Type[SupportsArgsProvider] = None,
            provider: 'ArgsProvider' = None,
            *,
            name: str = None,
            dest: str = None,
            prefix: str = None,
            no_provides: AbstractSet[str] = None
    ) -> None:
        no_provides = if_none_then(no_provides, set())
        if cls is None and provider is None:
            raise ArgumentError('Argument \'cls\' or \'provider\' must be provided.')
        if name is None:
            if cls is None:
                raise ArgumentError('Argument \'cls\' or \'name\' must be provided.')
            name = cls.__name__
            assert name is not None
        if dest is None:
            dest = name.replace('-', '_')
        if dest == '':
            raise ArgumentError('ChildProvider.dest must have '
                                'at least one character.')
        if prefix is None:
            prefix = name
        self._cls = cls
        self._provider = provider
        self.name = name
        self.dest = dest
        self.prefix = prefix
        self.no_provides = set(no_provides)

    def get_args_provider(self) -> 'ArgsProvider':
        if self._cls is not None:
            return self._cls.get_args_provider()
        else:
            assert self._provider is not None
            return self._provider
