from argparse import ArgumentParser as OriginalAP
from typing import Iterable, AbstractSet, Dict, Set, List, NamedTuple
from .arg_parse import ArgumentParser
from .namespace import Namespace
from .child_provider import ChildProvider
from .argument import Arg, PropagateState
from .parent_names_to_str import parent_names_to_str
from .exceptions import ConflictError


class _PropagateAttribute(NamedTuple):
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
        self._propagate_attributes: List[_PropagateAttribute] = list()
        arg_dests = [arg._dest for arg in self._args]
        arg_dests += [provider.dest for provider in self._child_providers]
        if len(arg_dests) != len(set(arg_dests)):
            # dest is non-unique; abort
            seen_dests: Set[str] = set()
            for dest in arg_dests:
                if dest in seen_dests:
                    raise ConflictError('argument or child provider {} have some conflicts!'
                                        .format(dest))
                seen_dests.add(dest)

    def add_arguments_to_parser(
            self,
            parser: OriginalAP
    ) -> None:
        self._add_arguments_recursively(root=self, parser=parser,
                                        parent_names=[''], parent_dists=list(),
                                        argument_prefixes=list(),
                                        propagate_data=dict(), prohibited_args=dict(),
                                        no_provides=set())
        if isinstance(parser, ArgumentParser):
            parser.register_deferring_action(self.apply_propagations)

    def _add_arguments_recursively(
            self,
            root: 'ArgsProvider',
            parser: OriginalAP,
            parent_names: List[str],
            parent_dists: List[str],
            argument_prefixes: List[str],
            propagate_data: Dict[str, str],
            prohibited_args: Dict[str, str],
            no_provides: AbstractSet[str]
    ) -> None:
        new_propagate_data: Dict[str, str] = dict()
        new_prohibited_args: Dict[str, str] = dict()
        group_name = parent_names_to_str(parent_names)
        argument_group = parser.add_argument_group(group_name)
        for arg in self._args:
            if arg.main_name in no_provides:
                continue
            returns = arg._pr_add_argument(argument_target=argument_group,
                                           parent_names=parent_names,
                                           parent_dists=parent_dists,
                                           argument_prefixes=argument_prefixes,
                                           propagate_data=propagate_data,
                                           prohibited_args=prohibited_args)
            state = returns.state
            if state is PropagateState.ForPropagate:
                # ready for propagate
                for target in returns.targets:
                    new_propagate_data[target] = returns.dest
            elif state is PropagateState.Prohibit:
                # ready for prohibit
                for target in returns.targets:
                    new_prohibited_args[target] = parent_names_to_str(parent_names + [target])
            elif state is PropagateState.Propagated:
                # set to propagate the value
                assert returns.propagated_from is not None
                attribute = _PropagateAttribute(source=returns.propagated_from,
                                                target=returns.dest)
                root._propagate_attributes.append(attribute)
        new_propagate_data.update(propagate_data)
        new_prohibited_args.update(prohibited_args)
        for child_provider in self._child_providers:
            provider = child_provider.cls.get_args_provider()
            new_parent_dists = parent_dists + [child_provider.dest]
            if child_provider.prefix == '':
                new_argument_prefixes = argument_prefixes
            else:
                new_argument_prefixes = argument_prefixes + [child_provider.prefix]
            if child_provider.name == '':
                new_parent_names = parent_names
            else:
                new_parent_names = parent_names + [child_provider.name]
            provider._add_arguments_recursively(root, parser,
                                                new_parent_names, new_parent_dists,
                                                new_argument_prefixes,
                                                new_propagate_data, new_prohibited_args,
                                                child_provider.no_provides)

    def apply_propagations(self, namespace: Namespace) -> None:
        for attribute in self._propagate_attributes:
            source = attribute.source
            target = attribute.target
            source_value = namespace._getattr_with_hierarchical_name(source)
            namespace._setattr_with_hierarchical_name(target, source_value)
