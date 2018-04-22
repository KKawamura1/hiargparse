import argparse
import re
from typing import Iterable, TypeVar, List, Tuple


hi_symbol_before = '--*--'
hi_symbol_after = '--@--'
hi_key = hi_symbol_before + '{}' + hi_symbol_after
hi_symbol_regexp = re.compile(r'^{}(.*?){}'.format(hi_symbol_before, hi_symbol_after))


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
