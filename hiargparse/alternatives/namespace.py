from argparse import Namespace as OriginalNS
from typing import Any, Dict, TypeVar, Mapping, Union, List, Generator, ClassVar, ItemsView
from hiargparse.hierarchy import parents_and_key_to_long_key, pop_highest_parent_name, iter_parents


SpaceT = TypeVar('SpaceT', bound=OriginalNS)


class Namespace(OriginalNS):
    """A variant of argparse.Namespace.

    A variant with which you can
    + easily access to its child provider
    + easily convert to / from dictionary
    + store data in its separate dictionary instead of direct access

    Its public methods are started with _ to follow collections.namedtuple.
    """

    _setattr_injection_key: ClassVar[str] = '==SETATTR-INJECTION-KEY=='

    def __init__(self, copy_from: Union[SpaceT, Mapping[str, Any]] = None) -> None:
        self._sequential_data: Dict[str, Any] = dict()
        self._hierarchical_data: Dict[str, Any] = dict()
        self.__set_injection()
        super().__init__()
        if copy_from is not None:
            self._update(copy_from)

    # override superclass attribute
    def _get_kwargs(self) -> ItemsView[str, Any]:
        return self._hierarchical_data.items()

    # access to attributes

    def __keycheck(self, key: Any) -> bool:
        if not isinstance(key, str):
            raise TypeError('key {} must be str, not {}'
                            .format(key, type(key)))
        return True

    def __setattr__(self, key: str, value: Any) -> None:
        # if injection-key not in self:
        try:
            object.__getattribute__(self, Namespace._setattr_injection_key)
        except AttributeError:
            # then call normal method
            super().__setattr__(key, value)
            return
        # otherwise method injection occurred
        self.__setattr_with_hierarchical_name(key, value)

    def __getattr__(self, key: str) -> Any:
        return self.__getattr_with_hierarchical_name(key)

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
        """Copy self and return it."""
        return type(self)(copy_from=self)

    def _update(
            self,
            contents: Union[OriginalNS, Mapping[str, Any]]
    ) -> None:
        """Overwrite self with given data."""
        if isinstance(contents, OriginalNS):
            self.__update_from_namespace(contents)
        else:
            self.__update_from_dict(contents)

    def _replaced(self: SpaceT, **kwargs: Any) -> SpaceT:
        """Return a copied self with its data replaced with given args."""
        target = self._copy()
        target._update(kwargs)
        return target

    def _asdict(self) -> Dict[str, Any]:
        """Convert self to an hierarchical dict and return it."""
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

    def __setattr_with_hierarchical_name(self, hierarchical_name: str, val: Any) -> None:
        """Set attribute.

        Key may be a long hierarchical name
        like <token>Foo</token><token>Bar</token>buz.
        We set the value as both the sequential (long-token-including-key: val)
        and hierarchical (key1: key2: key3: val) style.
        """
        assert self.__keycheck(hierarchical_name)
        if isinstance(val, OriginalNS):
            # Namespace cannot be attatched directly
            # because it may break the hierarchical structure.
            raise TypeError('value {} must not be Namespace, yours is {}'
                            .format(val, type(val)))
        # set sequential data
        self._sequential_data[hierarchical_name] = val

        # set hierarchical data
        child_name, remain_key = pop_highest_parent_name(hierarchical_name)
        if child_name is None:
            self._hierarchical_data[remain_key] = val
        else:
            if child_name not in self:
                self._hierarchical_data[child_name] = type(self)()  # initialize with Namespace
            assert isinstance(self[child_name], Namespace)
            self[child_name][remain_key] = val  # recursively registering

    def __getattr_with_hierarchical_name(self, hierarchical_name: str) -> Any:
        """Get attribute.

        Key may be a long hierarchical name
        like <token>Foo</token><token>Bar</token>buz.
        If the key in sequential data, it must not be a Namespace,
        so return seq[key].
        Otherwise, it may be in hierarchical data, so we search it.
        If there is no match, raise AttributeError.
        """
        # escape infinit recursion
        sequential_data = object.__getattribute__(self, '_sequential_data')

        # search in sequential data
        if hierarchical_name in sequential_data:
            val = sequential_data[hierarchical_name]
            return val
        # search in hierarchical data
        try:
            target = self
            remains = hierarchical_name
            for parent, remains in iter_parents(hierarchical_name):
                hierarchical_data = object.__getattribute__(target, '_hierarchical_data')
                target = hierarchical_data[parent]
            hierarchical_data = object.__getattribute__(target, '_hierarchical_data')
            val = hierarchical_data[remains]
            assert isinstance(val, Namespace)
            return val
        except KeyError as exc:
            # no such attribute; abort
            error_msg = ('\'{}\' object has no attribute \'{}\''
                         .format(type(self), hierarchical_name))
            raise AttributeError(error_msg) from None

    def __set_injection(self) -> None:
        super().__setattr__(Namespace._setattr_injection_key, None)

    def __unset_injection(self) -> None:
        try:
            super().__delattr__(Namespace._setattr_injection_key)
        except AttributeError:
            pass

    def __update_from_namespace(
            self,
            contents: OriginalNS
    ) -> None:
        if isinstance(contents, Namespace):
            copy_from = contents._sequential_data
        else:
            copy_from = contents.__dict__
        self.__update_from_dict(copy_from, converts_dict=False)

    def __update_from_dict(
            self,
            contents: Mapping[str, Any],
            converts_dict: bool = True
    ) -> None:
        self.__update_from_dict_recur(contents, converts_dict, parents=[])

    def __update_from_dict_recur(
            self,
            contents: Mapping[str, Any],
            converts_dict: bool,
            parents: List[str]
    ) -> None:
        for key, val in contents.items():
            if isinstance(val, dict) and converts_dict:
                new_parents = parents + [key]
                self.__update_from_dict_recur(val, converts_dict, new_parents)
            else:
                new_key = parents_and_key_to_long_key(parents, key)
                self[new_key] = val
