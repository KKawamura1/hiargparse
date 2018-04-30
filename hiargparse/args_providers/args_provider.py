from argparse import ArgumentParser as OriginalAP
from typing import Iterable, AbstractSet, Dict, Set, List, NamedTuple
from hiargparse import ArgumentParser, Namespace
from hiargparse.hierarchy import format_parent_names, format_parent_names_and_key
from hiargparse.file_protocols import dict_writers, dict_readers
from hiargparse.miscs import if_none_then
from .exceptions import ConflictError, ArgumentError
from .child_provider import ChildProvider
from .argument import Arg, PropagateState


class _PropagateAttribute(NamedTuple):
    """Propagate value from x to y"""
    source: str
    target: str


class ArgsProvider:
    """A class that provides values to Args.

    Use add_arguments_to_parser to register args.
    Also it supports writing to/ reading from files.

    Args:
        args: arguments you want to register.
        child_providers: providers you want to register as its children.
        propagate_args: syntax sugar for args with propagate=True.
    """

    def __init__(
            self,
            args: Iterable[Arg] = None,
            child_providers: Iterable[ChildProvider] = None,
            propagate_args: Iterable[Arg] = None
    ) -> None:
        args = if_none_then(args, [])
        child_providers = if_none_then(child_providers, [])
        propagate_args = if_none_then(propagate_args, [])
        self._args = list(args)
        if propagate_args:
            for arg in propagate_args:
                arg._pr_to_propagatable()
            self._args += propagate_args
        self._child_providers = child_providers
        self._propagate_attributes: List[_PropagateAttribute] = []
        arg_dests = [arg.dest for arg in self._args]
        arg_dests += [provider.dest for provider in self._child_providers]
        if len(arg_dests) != len(set(arg_dests)):
            # dest is non-unique; abort
            seen_dests: Set[str] = set()
            for dest in arg_dests:
                if dest in seen_dests:
                    raise ConflictError('argument or child provider {} have some conflicts!'
                                        .format(dest))
                seen_dests.add(dest)
        for child_provider in child_providers:
            if not child_provider.name:
                raise ArgumentError('child_provider must have a name '
                                    'with at least one character. ')

    def add_arguments_to_parser(
            self,
            parser: OriginalAP
    ) -> None:
        """Add its arguments to the given parser hierarchically."""
        self._add_arguments_recursively(root=self, parser=parser,
                                        writer=dict_writers.NullWriter(),
                                        parent_names=[''], parent_dists=[], argument_prefixes=[],
                                        propagate_data=dict(), prohibited_args=dict(),
                                        no_provides=set())
        if isinstance(parser, ArgumentParser):
            parser.register_deferring_action(self.apply_propagations)

    def write_out_configure_arguments(
            self,
            writer: dict_writers.AbstractDictWriter
    ) -> str:
        """Return a string that represents its all arguments as given style."""
        self._add_arguments_to_writer(writer)
        return writer.write_out()

    def read_configure_arguments(
            self,
            document: str,
            reader: dict_readers.AbstractDictReader,
            parser: OriginalAP = None
    ) -> Namespace:
        """Read the given document as given style and return the parameters."""
        parser = if_none_then(parser, ArgumentParser())
        contents = reader.to_normalized_dict(document)
        args: List[str] = []
        for key, val in contents.items():
            if val is None:
                continue
            args.append(key)
            if val is True or val is False:
                # maybe nargs = 0
                pass
            elif isinstance(val, (list, tuple)):
                for v in val:
                    args.append(str(v))
            else:
                args.append(str(val))
        self.add_arguments_to_parser(parser)
        name_space = parser.parse_args(args)
        return Namespace(name_space)

    def apply_propagations(self, namespace: Namespace) -> None:
        """Applying arguments propagation.

        Be sure to call this method after parser.parse_args().
        """
        for attribute in self._propagate_attributes:
            source = attribute.source
            target = attribute.target
            namespace[target] = namespace[source]

    # protected methods

    def _add_arguments_to_writer(
            self,
            writer: dict_writers.AbstractDictWriter
    ) -> None:
        self._add_arguments_recursively(root=self, parser=ArgumentParser(), writer=writer,
                                        parent_names=[''], parent_dists=[], argument_prefixes=[],
                                        propagate_data=dict(), prohibited_args=dict(),
                                        no_provides=set())

    def _add_arguments_recursively(
            self,
            root: 'ArgsProvider',
            parser: OriginalAP,
            writer: dict_writers.AbstractDictWriter,
            parent_names: List[str],
            parent_dists: List[str],
            argument_prefixes: List[str],
            propagate_data: Dict[str, str],
            prohibited_args: Dict[str, str],
            no_provides: AbstractSet[str]
    ) -> None:
        """Recursively collect informations and call arg._pr_add_argument."""
        new_propagate_data: Dict[str, str] = dict()
        new_prohibited_args: Dict[str, str] = dict()
        group_name = format_parent_names(parent_names)
        argument_group = parser.add_argument_group(group_name)
        for arg in self._args:
            if arg.main_name in no_provides:
                continue
            returns = arg._pr_add_argument(argument_target=argument_group,
                                           writer=writer,
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
                    new_prohibited_args[target] = format_parent_names_and_key(parent_names, target)
            elif state is PropagateState.Propagated:
                # set to propagate the value
                assert returns.propagated_from is not None
                attribute = _PropagateAttribute(source=returns.propagated_from,
                                                target=returns.dest)
                root._propagate_attributes.append(attribute)
        new_propagate_data.update(propagate_data)
        new_prohibited_args.update(prohibited_args)
        for child_provider in self._child_providers:
            provider = child_provider.get_args_provider()
            new_parent_dists = parent_dists + [child_provider.dest]
            if child_provider.prefix == '':
                new_argument_prefixes = argument_prefixes
            else:
                new_argument_prefixes = argument_prefixes + [child_provider.prefix]
            new_parent_names = parent_names + [child_provider.name]
            with writer.make_section(child_provider.name):
                provider._add_arguments_recursively(root=root, parser=parser, writer=writer,
                                                    parent_names=new_parent_names,
                                                    parent_dists=new_parent_dists,
                                                    argument_prefixes=new_argument_prefixes,
                                                    propagate_data=new_propagate_data,
                                                    prohibited_args=new_prohibited_args,
                                                    no_provides=child_provider.no_provides)
