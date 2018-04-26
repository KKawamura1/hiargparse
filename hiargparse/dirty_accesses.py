import argparse
from typing import List, Tuple


class DirtyAccessToArgparse:
    """Treats all non-public accesses to argparse."""

    ArgumentGroup = argparse._ArgumentGroup

    help_instance = argparse.HelpFormatter(prog='')

    @staticmethod
    def expand_help_text_from_action(action: argparse.Action) -> str:
        help_text: str = DirtyAccessToArgparse.help_instance._expand_help(action)  # type: ignore
        return help_text

    @staticmethod
    def get_metavar_from_optional_action(action: argparse.Action) -> List[str]:

        default_metavar: str = (DirtyAccessToArgparse  # type: ignore
                                .help_instance
                                ._get_default_metavar_for_optional(action))
        metavar_size = 1
        metavars: Tuple[str, ...] = (DirtyAccessToArgparse  # type: ignore
                                     .help_instance
                                     ._metavar_formatter(action, default_metavar)
                                     (metavar_size))
        return list(metavars)
