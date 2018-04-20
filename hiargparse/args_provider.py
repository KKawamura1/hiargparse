import argparse
import hiargparse
from typing import Iterable, AbstractSet
from typing import Dict, Set, List, NamedTuple
from .child_provider import ChildProvider
from .argument import Arg, PropagateState


class _DeferringAttribute(NamedTuple):
    source: str
    target: str


class ArgsProvider:
    def __init__(
            self,
            args: Iterable[Arg] = list(),
            child_providers: Iterable[ChildProvider] = list(),
            propagate_args: Iterable[Arg] = list()
    ) -> None:
        self._args = list(args)
        if propagate_args:
            for arg in propagate_args:
                arg._pr_to_propagatable()
            self._args += propagate_args
        self._child_providers = child_providers
        self._deferring_attributes: List[_DeferringAttribute] = list()

    def add_arguments(
            self,
            parser: argparse.ArgumentParser
    ) -> None:
        self._add_arguments_recursively(self, parser,
                                        list(), list(), list(), dict(), set(), set())
        if isinstance(parser, hiargparse.ArgumentParser):
            parser.register_deferring_action(self.apply_deferring_actions)

    def _add_arguments_recursively(
            self,
            root: 'ArgsProvider',
            parser: argparse.ArgumentParser,
            namespace_parents: List[str],
            arguments_prefixes: List[str],
            help_text_prefixes: List[str],
            propagate_data: Dict[str, str],
            prohibited_args: Set[str],
            no_provides: AbstractSet[str]
    ) -> None:
        new_propagate_data: Dict[str, str] = dict()
        new_prohibited_args: Set[str] = set()
        for arg in self._args:
            if arg.main_name in no_provides:
                continue
            returns = arg._pr_add_argument(parser, namespace_parents,
                                           arguments_prefixes, help_text_prefixes,
                                           propagate_data, prohibited_args)
            state = returns.state
            if state is PropagateState.ForPropagate:
                # ready for propagate
                for target in returns.targets:
                    new_propagate_data[target] = returns.dest
            elif state is PropagateState.Prohibit:
                # ready for prohibit
                new_prohibited_args |= set(returns.targets)
            elif state is PropagateState.Propagated:
                # set to propagate the value
                assert returns.propagated_from is not None
                attribute = _DeferringAttribute(source=returns.propagated_from,
                                                target=returns.dest)
                root._deferring_attributes.append(attribute)
        new_propagate_data.update(propagate_data)
        new_prohibited_args |= prohibited_args
        for child_provider in self._child_providers:
            provider = child_provider.cls.get_args_provider()
            new_namespace_parents = namespace_parents + [child_provider.dest]
            if child_provider.prefix == '':
                new_arguments_prefixes = arguments_prefixes
            else:
                new_arguments_prefixes = arguments_prefixes + [child_provider.prefix]
            if child_provider.name == '':
                new_help_text_prefixes = help_text_prefixes
            else:
                new_help_text_prefixes = help_text_prefixes + [child_provider.name]
            provider._add_arguments_recursively(root, parser, new_namespace_parents,
                                                new_arguments_prefixes, new_help_text_prefixes,
                                                new_propagate_data, new_prohibited_args,
                                                child_provider.no_provides)

    def apply_deferring_actions(self, namespace: argparse.Namespace) -> None:
        for attribute in self._deferring_attributes:
            source = attribute.source
            target = attribute.target
            assert hasattr(namespace, source)
            setattr(namespace, target, getattr(namespace, source))
