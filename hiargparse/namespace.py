from argparse import Namespace as OriginalNS
from typing import Any, Dict, TypeVar, Mapping, Union, Type
from .hierarchy import split_child_names_and_key


SpaceT = TypeVar('SpaceT', bound=OriginalNS)


class Namespace(OriginalNS):
    """A variant of argparse.Namespace

    A variant with which you can
    + easily access to its child provider
    + easily convert to / from dictionary
    """

    def __init__(self, copy_from: Union[SpaceT, Mapping[str, Any]] = None) -> None:
        super().__init__()
        if copy_from is not None:
            self._update(copy_from)

    # normalization from inline hierarchy to nested namespace
    def _normalized(self: SpaceT, converts_dict: bool = True) -> SpaceT:
        target = type(self)()
        for long_key, val in self.__dict__.items():
            child_names, key = split_child_names_and_key(long_key)
            now_target = target
            for child_name in child_names:
                if child_name not in now_target:
                    now_target[child_name] = type(self)()
                assert isinstance(now_target[child_name], Namespace)
                now_target = now_target[child_name]
            now_target[key] = val
        return now_target

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

    def _copy(self: SpaceT) -> SpaceT:
        return type(self)(copy_from=self)

    def _update(
            self,
            contents: Union[OriginalNS, Mapping[str, Any]],
            converts_dict: bool = None
    ) -> None:
        if isinstance(contents, OriginalNS):
            if converts_dict is None:
                self._update_from_namespace(contents)
            else:
                self._update_from_namespace(contents, converts_dict)
        else:
            if converts_dict is None:
                self._update_from_dict(contents)
            else:
                self._update_from_dict(contents, converts_dict)

    def _update_from_namespace(
            self,
            contents: OriginalNS,
            converts_dict: bool = False
    ) -> None:
        self._update_from_dict(contents.__dict__, converts_dict)

    def _update_from_dict(
            self,
            contents: Mapping[str, Any],
            converts_dict: bool = True
    ) -> None:
        for key, val in contents.items():
            target: Any = val
            if isinstance(val, dict):
                if converts_dict:
                    target = type(self)()
                    target._update(val, converts_dict)
            self[key] = target

    def _replaced(self: SpaceT, **kwargs: Any) -> SpaceT:
        target = self._copy()
        target._update(kwargs)
        return target

    @classmethod
    def make(cls: Type[SpaceT], contents: Mapping[str, Any]) -> SpaceT:
        namespace = cls()
        return namespace._update(contents)

    def _asdict(self) -> Dict[str, Any]:
        normalized = self._normalize()
        ret_dict: Dict[str, Any] = dict()
        for key, val in normalized.__dict__.items():
            if isinstance(val, Namespace):
                val = val._asdict()
            ret_dict[key] = val
        return ret_dict
