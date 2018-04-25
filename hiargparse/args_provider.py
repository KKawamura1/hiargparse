import argparse
from argparse import ArgumentParser as OriginalAP
from typing import Iterable, AbstractSet, Dict, Set, List, NamedTuple, Callable, Any
from pathlib import Path
from .arg_parse import ArgumentParser
from .namespace import Namespace
from .child_provider import ChildProvider
from .argument import Arg, PropagateState
from .parent_names_to_str import parent_names_to_str
from .exceptions import ConflictError, ArgumentError
from . import dict_writers, dict_readers
from .configure_file_type import ConfigureFileType


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
        for child_provider in child_providers:
            if not child_provider.name:
                raise ArgumentError('child_provider must have a name '
                                    'with at least one character. ')

    def add_arguments_to_parser(
            self,
            parser: OriginalAP
    ) -> None:
        self._add_arguments_recursively(root=self, parser=parser)
        if isinstance(parser, ArgumentParser):
            parser.register_deferring_action(self.apply_propagations)

    def write_out_configure_arguments(
            self,
            file_type: ConfigureFileType
    ) -> str:
        # access to protected attributes
        help_instance = argparse.HelpFormatter(prog='')
        expand_help_text_from_action: Callable[[argparse.Action], str]
        expand_help_text_from_action = help_instance._expand_help  # type: ignore

        def get_metavar_from_action(action: argparse.Action) -> str:
            assert action.option_strings
            # access to protected attributes
            tmp: Any = help_instance._get_default_metavar_for_optional(action)  # type: ignore
            default_metavar: str = tmp
            tmp: Any = help_instance._metavar_formatter(action, default_metavar)  # type: ignore
            metavar: str = tmp(1)[0]
            return metavar

        writer: dict_writers.AbstractDictWriter
        if file_type is ConfigureFileType.toml:
            writer = dict_writers.TOMLWriter(expand_help_text_from_action,
                                             get_metavar_from_action)
        elif file_type is ConfigureFileType.yaml:
            writer = dict_writers.YAMLWriter(expand_help_text_from_action,
                                             get_metavar_from_action)
        self._add_arguments_to_writer(writer)
        return writer.write_out()

    def read_configure_arguments(
            self,
            document: str,
            file_type: ConfigureFileType,
            parser: OriginalAP = ArgumentParser()
    ) -> Namespace:
        reader: dict_readers.AbstractDictReader
        if file_type is ConfigureFileType.toml:
            raise
        elif file_type is ConfigureFileType.yaml:
            reader = dict_readers.YAMLReader()
        contents = reader.to_normalized_dict(document)
        args: List[str] = list()
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
        print(args)
        self.add_arguments_to_parser(parser)
        name_space = parser.parse_args(args)
        return Namespace(name_space)

    def _add_arguments_to_writer(
            self,
            writer: dict_writers.AbstractDictWriter
    ) -> None:
        self._add_arguments_recursively(root=self, writer=writer)

    def _add_arguments_recursively(
            self,
            root: 'ArgsProvider',
            parser: OriginalAP = ArgumentParser(),
            writer: dict_writers.AbstractDictWriter = dict_writers.NullWriter(),
            parent_names: List[str] = [''],
            parent_dists: List[str] = list(),
            argument_prefixes: List[str] = list(),
            propagate_data: Dict[str, str] = dict(),
            prohibited_args: Dict[str, str] = dict(),
            no_provides: AbstractSet[str] = set()
    ) -> None:
        new_propagate_data: Dict[str, str] = dict()
        new_prohibited_args: Dict[str, str] = dict()
        group_name = parent_names_to_str(parent_names)
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
            new_parent_names = parent_names + [child_provider.name]
            with writer.make_section(child_provider.name):
                provider._add_arguments_recursively(root=root, parser=parser, writer=writer,
                                                    parent_names=new_parent_names,
                                                    parent_dists=new_parent_dists,
                                                    argument_prefixes=new_argument_prefixes,
                                                    propagate_data=new_propagate_data,
                                                    prohibited_args=new_prohibited_args,
                                                    no_provides=child_provider.no_provides)

    def apply_propagations(self, namespace: Namespace) -> None:
        for attribute in self._propagate_attributes:
            source = attribute.source
            target = attribute.target
            namespace[target] = namespace[source]
