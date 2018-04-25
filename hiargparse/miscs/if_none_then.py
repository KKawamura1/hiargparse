from typing import Optional, TypeVar


T = TypeVar('T')


def if_none_then(value: Optional[T], default: T) -> T:
    """If value is not None, return value; otherwise return default.

    Tipical usage is:

        def fn(list_plz: List[Foo] = []) -> None:  # this is BAD!
            ...

        def fn(list_plz: List[Foo] = None) -> None:
            list_plz = set_mutable_default(list_plz, [])  # this is GOOD
            ...

    """
    if value is not None:
        return value
    return default
