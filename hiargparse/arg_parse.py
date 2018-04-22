from argparse import ArgumentParser as OriginalAP
from argparse import Namespace as OriginalNS
from .namespace import Namespace

from typing import Any, Sequence, Tuple, List, Callable


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
        return Namespace(params), remains

    def register_deferring_action(
            self,
            action: Callable[[Namespace], None]
    ) -> None:
        self._defer_actions.append(action)

    def parse_args(
            self,
            args: Sequence[str] = None,
            namespace: OriginalNS = None
    ) -> Namespace:
        params = Namespace(super().parse_args(args, namespace))
        self._do_deferred_actions(params)
        return params._normalized()

    def _do_deferred_actions(self, params: Namespace) -> None:
        for action in self._defer_actions:
            action(params)
