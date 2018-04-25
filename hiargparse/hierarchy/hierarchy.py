import argparse
import re
from typing import Iterable, TypeVar, List, Tuple, Optional, Generator


hi_symbol_before = '--*--'
hi_symbol_after = '--@--'
hi_symbols = (hi_symbol_before, hi_symbol_after)
hi_key = hi_symbol_before + '{}' + hi_symbol_after
hi_symbol_regexp = re.compile(r'{}(.*?){}'.format(*[re.escape(symb) for symb in hi_symbols]))


SpaceT = TypeVar('SpaceT', bound=argparse.Namespace)


def parents_and_key_to_long_key(parents: Iterable[str], key: str) -> str:
    retstr = str()
    for parent in parents:
        retstr += hi_key.format(parent)
    retstr += key
    return retstr


def pop_highest_parent_name(name: str) -> Tuple[Optional[str], str]:
    match = hi_symbol_regexp.search(name)
    if match is None:
        return None, name
    else:
        return match.group(1), name[match.end():]


def iter_parents(name: str) -> Generator[Tuple[str, str], None, None]:
    remains = name
    while True:
        parent, remains = pop_highest_parent_name(remains)
        if parent is not None:
            yield parent, remains
        else:
            raise StopIteration()


def long_key_to_parents_and_key(name: str) -> Tuple[List[str], str]:
    names: List[str] = list()
    remains = name
    for parent, remains in iter_parents(name):
        names.append(parent)
    return names, remains


def is_hierarchical_key(name: str) -> bool:
    return pop_highest_parent_name(name)[0] is not None
