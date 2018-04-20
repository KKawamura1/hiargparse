import argparse
import hiargparse
import enum
from typing import Iterable, AbstractSet, Type, Union, Sequence, Collection, Optional
from typing import Dict, Set, List, Any, NamedTuple
from typing_extensions import Protocol
from .hierarchy import get_child_dest_str


class SupportsArgsProvider(Protocol):
    """Structural subtyping protocol which supports ArgsProvider."""

    @classmethod
    def get_args_provider(cls) -> 'ArgsProvider':
        ...


class ChildProvider:
    def __init__(
            self,
            cls: Type[SupportsArgsProvider],
            name: str = None,
            dest: str = None,
            prefix: str = None,
            no_provides: AbstractSet[str] = set()
    ) -> None:
        if name is None:
            name = cls.__name__  # type: ignore
            assert name is not None
        if dest is None:
            dest = name.replace('-', '_')
        if dest == '':
            raise argparse.ArgumentTypeError('ChildProvider.dest must have '
                                             'at least one character!')
        if prefix is None:
            prefix = name
        self.cls = cls
        self.name = name
        self.dest = dest
        self.prefix = prefix
        self.no_provides = set(no_provides)


class _PropagateState(enum.Enum):
    ForPropagate = enum.auto()
    Propagated = enum.auto()
    Prohibit = enum.auto()
    Nothing = enum.auto()


class _AddArgumentReturn(NamedTuple):
    state: _PropagateState
    targets: List[str]
    dest: str
    propagated_from: Optional[str]


class Arg:
    def __init__(
            self,
            name: Union[str, Sequence[str]],
            default: Any,
            *,
            main_name: str = None,
            action: argparse.Action = None,
            type: Any = None,
            help: str = None,
            dest: str = None,
            metavar: str = None,
            propagate: bool = None,
            propagate_targets: Collection[str] = None,
            **kwargs: Any
    ) -> None:
        # names
        names: Collection[str]
        if isinstance(name, str):
            names = [name]
        else:
            names = name
        if not name:
            raise argparse.ArgumentTypeError('at least one name must be given')
        # main_name
        if main_name is None:
            main_name = names[0]
        # default, type
        if type is None:
            if default is not None:
                type = default.__class__
            else:
                raise argparse.ArgumentTypeError('type or default for argument {} must be given'
                                                 .format(main_name))
        # dest
        if dest is None:
            dest = main_name.replace('-', '_')
        # metavar
        if metavar is None:
            metavar = main_name.upper()
        # propagate targets
        if propagate_targets is None:
            propagate_targets = names
        # help_text
        default_help_text = '{}. '.format(main_name)
        if len(names) >= 2:
            default_help_text += '(a.k.a. {}) '.format(', '.join(names[1:]))
        if default is not None:
            default_help_text += 'default: %(default)s. '
        if help is None:
            help = default_help_text
        else:
            help = help.replace('%(default-text)s', default_help_text)
        self.main_name = main_name
        self._names = names
        self._default = default
        self._action = action
        self._type = type
        self._help = help
        self._dest = dest
        self._metavar = metavar
        self._propagate = propagate
        self._propagate_targets = list(propagate_targets)
        self._kwargs = kwargs

    def _pr_add_argument(
            self,
            parser: argparse.ArgumentParser,
            namespace_parents: List[str],
            arguments_prefixes: List[str],
            help_text_prefixes: List[str],
            propagate_data: Dict[str, str],
            prohibited_args: Set[str],
    ) -> _AddArgumentReturn:
        """add arguments to given parser.

        protected (visible only in this module).
        """
        # argument names
        names = list()
        for name in self._names:
            argument_flagments = list(arguments_prefixes) + [name]
            names.append('--{}'.format('-'.join(argument_flagments)))

        # dest
        dest = get_child_dest_str(namespace_parents) + self._dest

        # keyword arguments for parser
        parser_kwargs = {key: val for key, val in self._kwargs.items()}
        if self._default is not None:
            parser_kwargs['default'] = self._default
        parser_kwargs['type'] = self._type
        if self._action is not None:
            parser_kwargs['action'] = self._action
        parser_kwargs['help'] = '/{}: {}'.format('/'.join(help_text_prefixes), self._help)
        parser_kwargs['dest'] = dest
        parser_kwargs['metavar'] = self._metavar

        # propagate check
        propagate_state: _PropagateState
        propagated_from: Optional[str] = None
        # if at least one name is in propagate_args, then use it
        # (not add a new argument to the parser)
        if any([name in propagate_data for name in self._names]):
            propagate_state = _PropagateState.Propagated
            propagated_from_set = {propagate_data[name] for name in self._names
                                   if name in propagate_data}
            if len(propagated_from_set) != 1:
                # must be >= 2
                assert propagated_from_set
                # raise conflict error
                raise argparse.ArgumentTypeError(
                    ('argument {} ([{}]) has more than 1 deferent propagation. '
                     ).format(self.main_name, ', '.join(self._names))
                )
            propagated_from = list(propagated_from_set)[0]
        elif any([name in prohibited_args for name in self._names]):
            # if at least one name is in prohibited_args, then abort
            prohibited_name = [name for name in self._names if name in prohibited_args][0]
            raise argparse.ArgumentTypeError(
                ('name {} has conflicts; '
                 'please specify propagate=True '
                 'if this conflict is your desirable operation. '
                 ).format(prohibited_name)
            )
        else:
            # otherwise add the argument
            parser.add_argument(*names, **parser_kwargs)

            # return propagate states
            if self._propagate is None:
                # child parsers cannot have the same argument
                propagate_state = _PropagateState.Prohibit
            elif self._propagate:
                # explicitly propagate to child parsers
                propagate_state = _PropagateState.ForPropagate
            else:
                # no registration; child parsers can have the same argument without any warnings
                propagate_state = _PropagateState.Nothing
        return _AddArgumentReturn(state=propagate_state, targets=self._propagate_targets,
                                  dest=dest, propagated_from=propagated_from)

    def _pr_to_propagatable(self) -> None:
        if self._propagate is not None and not self._propagate:
            raise argparse.ArgumentTypeError('do not specify propagate=False '
                                             'to propagate_arg. ')
        self._propagate = True


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
            if state is _PropagateState.ForPropagate:
                # ready for propagate
                for target in returns.targets:
                    new_propagate_data[target] = returns.dest
            elif state is _PropagateState.Prohibit:
                # ready for prohibit
                new_prohibited_args |= set(returns.targets)
            elif state is _PropagateState.Propagated:
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
