from typing import Mapping, Any, Dict


def added_double_hyphen(contents: Mapping[str, Any]) -> Dict[str, Any]:
    """add double hyphen ('--') to all keys and return it"""
    target: Dict[str, Any] = dict()
    for key, val in contents.items():
        new_key = '--' + key
        target[new_key] = val

    return target
