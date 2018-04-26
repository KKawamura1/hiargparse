from typing import Sequence


def format_parent_names(parent_names: Sequence[str]) -> str:
    """return human-readable string repr with given names"""
    return ''.join(['{}/'.format(name) for name in parent_names])


def format_parent_names_and_key(parent_names: Sequence[str], key: str) -> str:
    return format_parent_names(list(parent_names) + [key])
