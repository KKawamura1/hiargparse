from argparse import Namespace as OriginalNS
from typing import Any, Dict, TypeVar, Mapping, Union, Type, List, NamedTuple, Generator
from .hierarchy import split_child_names_and_key


SpaceT = TypeVar('SpaceT', bound=OriginalNS)


class Namespace(OriginalNS):
    """A variant of argparse.Namespace

    A variant with which you can
    + easily access to its child provider
    + easily convert to / from dictionary
    + store data in its separate dictionary instead of direct access
    """

    def __init__(self, copy_from: Union[SpaceT, Mapping[str, Any]] = None) -> None:
        super().__init__()
        self._sequential_data: Dict[str, Any] = dict()
        self._hierarchical_data: Dict[str, Any] = dict()
        if copy_from is not None:
            self._update(copy_from)

    # override superclass attribute
    def _get_kwargs(self) -> Dict[str, Any]:
        return self._hierarchical_data

    # access to attributes

    def __keycheck(self, key: Any) -> bool:
        if not isinstance(key, str):
            raise TypeError('key {} must be str, not {}'
                            .format(key, type(key)))
        return True

    def __setattr__(self, key: str, value: Any) -> None:
        self._setattr_with_hierarchical_name(key, value)

    def __getattr__(self, key: str) -> Any:
        return self._getattr_with_hierarchical_name(key)

    def __delattr__(self, key: str) -> None:
        raise TypeError('{} object does not support __delattr__ method. '
                        .format(type(self)))

    # dict compatibility

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __delitem__(self, key: str) -> None:
        delattr(self, key)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def __len__(self) -> int:
        return len(self._sequential_data)

    def __iter__(self) -> Generator[Any, None, None]:
        """implemented for compatibility with collections.abc.Mapping.

        Returns only values (not key).
        """
        for key, value in self._sequential_data.items():
            yield value
        raise StopIteration()

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
        if isinstance(contents, Namespace):
            copy_from = contents._sequential_data
        else:
            copy_from = contents._get_kwargs()
        self._update_from_dict(copy_from, converts_dict)

    def _update_from_dict(
            self,
            contents: Mapping[str, Any],
            converts_dict: bool = True
    ) -> None:
        for key, val in contents.items():
            target: Any
            if isinstance(val, dict) and converts_dict:
                target = type(self)()
                target._update(val, converts_dict)
            else:
                target = val
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
        ret_dict: Dict[str, Any] = dict()
        for key, val in self._hierarchical_data.items():
            if isinstance(val, Namespace):
                val = val._asdict()
            ret_dict[key] = val
        return ret_dict

    def __str__(self) -> str:
        type_name = type(self).__name__
        arg_strings: List[str] = list()
        namespace_children: Dict[str, 'Namespace'] = dict()
        for key, val in self._get_kwargs():
            if key.isidentifier():
                key_str = key
            else:
                key_str = '\"{}\"'.format(key)
            if isinstance(val, Namespace):
                # defer namespaces to print them final
                namespace_children[key_str] = val
            else:
                arg_strings.append('{}: {}'.format(key_str, str(val)))
        for key_str, child in namespace_children.items():
            arg_strings.append('{}: {}'.format(key_str, str(child)))
        arg_string = '\n' + ', \n'.join(arg_strings)
        arg_string = arg_string.replace('\n', '\n ') + '\n'
        return "{}({})".format(type_name, arg_string)

    # protected methods

    def _setattr_with_hierarchical_name(self, hierarchical_name: str, val: Any) -> None:
        """set attribute

        Key may be a long hierarchical name
        like <token>Foo</token><token>Bar</token>buz .
        We set the value as both the sequential (long-token-including-key: val)
        and hierarchical (key1: key2: key3: val) style.
        """
        assert self.__keycheck(hierarchical_name)
        if isinstance(val, OriginalNS):
            # Namespace cannot be attatched directly
            # because it may break the hierarchical structure.
            raise TypeError('value {} must not be Namespace, yours is {}'
                            .format(val, type(val)))
        self._sequential_data[hierarchical_name] = val
        target = self
        child_names, key = split_child_names_and_key(hierarchical_name)
        for child_name in child_names:
            if child_name not in target:
                target._hierarchical_data[child_name] = type(self)()  # initialize with Namespace
            target = target._hierarchical_data[child_name]
        target._hierarchical_data[key] = val

    def _getattr_with_hierarchical_name(self, hierarchical_name: str) -> Any:
        """get attribute

        Key may be a long hierarchical name
        like <token>Foo</token><token>Bar</token>buz .
        If the key in sequential data, it must not be a Namespace,
        so return seq[key].
        Otherwise, it may be in hierarchical data, so we search it.
        If there is no match, raise AttributeError.
        """
        # search in sequential data
        if hierarchical_name in self._sequential_data:
            val = self._sequential_data[hierarchical_name]
            return val
        # search in hierarchical data
        try:
            target = self
            child_names, key = split_child_names_and_key(hierarchical_name)
            for child_name in child_names:
                target = target._hierarchical_data[child_name]
            val = target._hierarchical_data[key]
            assert isinstance(val, Namespace)
            return val
        except KeyError as exc:
            # no such attribute; abort
            error_msg = ('\'{}\' object has no attribute \'{}\''
                         .format(type(self), hierarchical_name))
            raise AttributeError(error_msg) from None
