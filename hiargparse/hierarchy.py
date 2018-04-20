import argparse
from typing import Iterable, TypeVar, List, Dict, Any, Mapping, cast


hi_symbol = '--*--'
hi_key = hi_symbol + '{}' + '-'


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


def is_attr_name(name: str) -> bool:
    return name[:len(hi_symbol)] != hi_symbol


def namespace_to_dict(namespace: SpaceT) -> Dict[str, Any]:
    ret_dict: Dict[str, Any] = dict()
    for attr_name, val in namespace.__dict__.items():
        if is_attr_name(attr_name):
            ret_dict[attr_name] = val
    return ret_dict


def dict_to_namespace(
        contents: Mapping[str, Any],
        namespace: SpaceT = None
) -> SpaceT:
    if namespace is not None:
        target = namespace
    else:
        target = cast(SpaceT, argparse.Namespace())
    _dict_to_namespace_recur(contents, target, list())
    return target


def _dict_to_namespace_recur(
        contents: Mapping[str, Any],
        namespace: SpaceT,
        parents: List[str]
) -> None:
    dest = get_child_dest_str(parents)
    for key, val in contents.items():
        if isinstance(val, dict):
            # create child namespace
            _dict_to_namespace_recur(val, namespace, parents + [key])
        else:
            key_str = dest + key
            setattr(namespace, key_str, val)
