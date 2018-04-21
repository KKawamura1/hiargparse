from typing import List


def parent_names_to_str(parent_names: List[str]) -> str:
    return ''.join(['{}/'.format(name) for name in parent_names])
