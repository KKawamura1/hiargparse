from typing import Any, Sequence, Tuple, List, Callable, cast, TYPE_CHECKING
from argparse import ArgumentParser as OriginalAP
from argparse import Namespace as OriginalNS
from .namespace import Namespace

if TYPE_CHECKING:
    from hiargparse.args_providers import ArgsProvider


class ArgumentParser(OriginalAP):
    """A wrapper class for argparse.ArgumentParser.

    Do some cleanups for hiargparse.ArgsProviders
    and returns hiargparse.Namespace instead of argparse.Namespace.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._defer_actions: List[Callable[[Namespace], None]] = list()

    def parse_known_args(
            self,
            args: Sequence[str] = None,
            namespace: OriginalNS = None
    ) -> Tuple[Namespace, List[str]]:
        """Wrapper method to return hiargparse.Namespace.

        This method also takes some weird cleanups that hiargparse requires.
        """
        if namespace is None:
            target_space = Namespace()
        else:
            target_space = Namespace(namespace)
        params, remains = super().parse_known_args(args, target_space)
        # I know this params has type hiargparse.Namespace instead of argparse.Namespace
        # typeshed lacks some important features
        params = cast(Namespace, params)
        self._do_deferred_actions(params)
        return params, remains

    def parse_args(
            self,
            args: Sequence[str] = None,
            namespace: OriginalNS = None
    ) -> Namespace:
        """Wrapper method to return hiargparse.Namespace."""
        params = super().parse_args(args, namespace)
        # I know this params has type hiargparse.Namespace instead of argparse.Namespace
        params = cast(Namespace, params)
        return params

    def add_arguments_from_provider(
            self,
            provider: 'ArgsProvider'
    ) -> None:
        """Syntax sugar for args_provider.add_arguments_to_parser()."""
        provider.add_arguments_to_parser(self)

    def register_deferring_action(
            self,
            action: Callable[[Namespace], None]
    ) -> None:
        """Register an action to do after its parsing."""
        self._defer_actions.append(action)

    def get_default_parameters(self) -> Namespace:
        """Get defaults by passing no arguments to the parser."""
        return self.parse_args(args=[])

    # protected

    def _do_deferred_actions(self, params: Namespace) -> None:
        for action in self._defer_actions:
            action(params)
