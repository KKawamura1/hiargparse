import argparse
from typing import Any, Dict, TypeVar, Mapping
from .hierarchy import get_child_namespace, namespace_to_dict, dict_to_namespace


class Namespace(argparse.Namespace):
    """A variant of argparse.Namespace

    A variant with which you can
    + easily access to its child provider
    + easily convert to / from dictionary
    """

    SpaceT = TypeVar('SpaceT', bound=argparse.Namespace)

    def __init__(self, copy_from: SpaceT = None) -> None:
        super().__init__()
        if copy_from is not None:
            for key, val in copy_from.__dict__.items():
                setattr(self, key, val)

    # access to its child provider

    def _get_child(self, key: str) -> 'Namespace':
        return get_child_namespace(self, key)

    # dict compatibility

    def __keycheck(self, key: Any) -> None:
        if not isinstance(key, str):
            raise TypeError('key {} must be str, not {}'
                            .format(key, type(key)))

    def __getitem__(self, key: str) -> Any:
        self.__keycheck(key)
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__keycheck(key)
        setattr(self, key, value)

    def __delitem__(self, key: str) -> None:
        self.__keycheck(key)
        delattr(self, key)

    # useful conversion methods
    # referring to collections.namedtuple

    def _update(self, contents: Mapping[str, Any]) -> 'Namespace':
        return dict_to_namespace(contents, self)

    def _replace(self, **kwargs: Any) -> 'Namespace':
        return self._update(kwargs)

    @classmethod
    def _make(cls, contents: Mapping[str, Any]) -> 'Namespace':
        namespace = Namespace()
        return namespace._update(contents)

    def _asdict(self) -> Dict[str, Any]:
        return namespace_to_dict(self)
