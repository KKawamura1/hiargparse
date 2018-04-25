from typing import Callable, Mapping, MutableMapping, Any
from collections.abc import Mapping as MappingClass


def concat_with_hyphen(*keys: str) -> str:
    return '-'.join([key for key in keys if key])


def normalize_dict(
        contents: Mapping[str, Any],
        target: MutableMapping[str, Any],
        parent_key: str = '',
        concat_parents: Callable[[str, str], str] = concat_with_hyphen,
        concat_child: Callable[[str, str], str] = concat_with_hyphen
) -> None:
    for key, val in contents.items():
        if isinstance(val, MappingClass):
            new_parent_key = concat_parents(parent_key, key)
            normalize_dict(val, target, new_parent_key,
                           concat_parents, concat_child)
        else:
            new_assign_key = concat_child(parent_key, key)
            target[new_assign_key] = val
