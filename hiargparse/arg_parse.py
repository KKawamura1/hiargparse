from typing import Any, Sequence, Tuple, List, Callable, cast, TYPE_CHECKING
from argparse import ArgumentParser as OriginalAP
from argparse import Namespace as OriginalNS
import argparse
from pathlib import Path
from .namespace import Namespace
from .configure_file_type import ConfigureFileType
from .formatters import TOMLFormatter

if TYPE_CHECKING:
    from .args_provider import ArgsProvider


class ArgumentParser(OriginalAP):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._defer_actions: List[Callable[[Namespace], None]] = list()

    def parse_known_args(
            self,
            args: Sequence[str] = None,
            namespace: OriginalNS = None
    ) -> Tuple[Namespace, List[str]]:
        """argparse.Namespace to hiargparse.Namespace"""
        params, remains = super().parse_known_args(args, namespace)
        params = Namespace(params)._normalized()
        self._do_deferred_actions(params)
        return params, remains

    def parse_args(
            self,
            args: Sequence[str] = None,
            namespace: OriginalNS = None
    ) -> Namespace:
        params = super().parse_args(args, namespace)
        # I know this params has type hiargparse.Namespace instead of argparse.Namespace
        params = cast(Namespace, params)
        return params

    def add_arguments_from_provider(
            self,
            provider: 'ArgsProvider'
    ) -> None:
        provider.add_arguments_to_parser(self)

    def register_deferring_action(
            self,
            action: Callable[[Namespace], None]
    ) -> None:
        self._defer_actions.append(action)

    def _do_deferred_actions(self, params: Namespace) -> None:
        for action in self._defer_actions:
            action(params)

    def get_default_parameters(self) -> Namespace:
        return self.parse_args(args=list())

    def write_configure_arguments(
            self,
            path: Path,
            file_type: ConfigureFileType
    ) -> None:
        formatter = TOMLFormatter()
        # little bad accesses to a protected attribute
        action_groups: List[argparse._ArgumentGroup] = self._action_groups  # type: ignore
        for action_group in action_groups:
            title: str = action_group.title  # type: ignore
            description: str = action_group.description  # type: ignore
            group_actions: List[argparse.Action] = action_group._group_actions  # type: ignore
            formatter.start_section(title)
            formatter.add_text(description)
            formatter.add_arguments(group_actions)
            formatter.end_section()

        print(formatter.format_help())
