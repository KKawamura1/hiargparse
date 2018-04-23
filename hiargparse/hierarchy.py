import argparse
import re
from typing import Iterable, TypeVar, List, Tuple, Mapping, Any, Dict


hi_symbol_before = '--*--'
hi_symbol_after = '--@--'
hi_symbols = (hi_symbol_before, hi_symbol_after)
hi_key = hi_symbol_before + '{}' + hi_symbol_after
hi_symbol_regexp = re.compile(r'{}(.*?){}'.format(*[re.escape(symb) for symb in hi_symbols]))


def get_child_dest_str(keys: Iterable[str]) -> str:
    retstr = str()
    for key in keys:
        retstr += hi_key.format(key)
    return retstr


SpaceT = TypeVar('SpaceT', bound=argparse.Namespace)


def get_child_namespace(namespace: SpaceT, key: str) -> SpaceT:
    return_space = type(namespace)()
    key_str = hi_key.format(key)
    for attr_name in dir(namespace):
        if attr_name[:len(key_str)] == key_str:
            setattr(return_space, attr_name[len(key_str):], getattr(namespace, attr_name))
    return return_space


def split_child_names_and_key(name: str) -> Tuple[List[str], str]:
    names: List[str] = list()
    last_end = 0
    for match in hi_symbol_regexp.finditer(name):
        assert match.start() == last_end
        names.append(match.group(1))
        last_end = match.end()
    return (names, name[last_end:])


def is_hierarchical_key(name: str) -> bool:
    return len(split_child_names_and_key(name)[0]) > 0


def resolve_nested_dict(contents: Mapping[str, Any]) -> Dict[str, Any]:
    """Convert a nested dictionary to an uniformed dictionary.

    ex.\)
    input: dict(a=1, b=dict(c=2, d=dict(e=3)))
    output: dict(dest(a)=1, dest(b,c)=2, dest(b,d,e)=3)
    """

    target: Dict[str, Any] = dict()
    _resolve_nested_dict_recur(target, contents, list())
    return target


def _resolve_nested_dict_recur(
        target: Dict[str, Any],
        contents: Mapping[str, Any],
        parents: List[str]
) -> None:
    for key, val in contents.items():
        if isinstance(val, dict):
            _resolve_nested_dict_recur(target, contents=val,
                                       parents=(parents + [key]))
        else:
            dest = get_child_dest_str(parents + [key])
            target[dest] = val
