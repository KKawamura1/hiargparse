import argparse
import enum
from typing import Union, Sequence, Collection, Optional
from typing import Dict, Set, List, Any, NamedTuple
from .hierarchy import get_child_dest_str


ArgumentAccepter = Union[argparse.ArgumentParser, argparse._ArgumentGroup]


class PropagateState(enum.Enum):
    ForPropagate = enum.auto()
    Propagated = enum.auto()
    Prohibit = enum.auto()
    Nothing = enum.auto()


class _AddArgumentReturn(NamedTuple):
    state: PropagateState
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
        # type and help seem to conflict with python built-in
        # rename them not to confuse IDE
        arg_type = type
        help_text = help

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
        if arg_type is None:
            if default is not None:
                arg_type = default.__class__
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
        # if type is easy-to-understand one, then show it
        if arg_type in [int, str, float, bool]:
            default_help_text += 'type: %(type)s. '
        if default is not None:
            default_help_text += 'default: %(default)s. '
        if help_text is None:
            help_text = default_help_text
        else:
            help_text = help_text.replace('%(default-text)s', default_help_text)
        self.main_name = main_name
        self._names = names
        self._default = default
        self._action = action
        self._type = arg_type
        self._help = help_text
        self._dest = dest
        self._metavar = metavar
        self._propagate = propagate
        self._propagate_targets = list(propagate_targets)
        self._kwargs = kwargs

    def _pr_add_argument(
            self,
            argument_target: ArgumentAccepter,
            parent_names: List[str],
            parent_dists: List[str],
            argument_prefixes: List[str],
            propagate_data: Dict[str, str],
            prohibited_args: Set[str],
    ) -> _AddArgumentReturn:
        """add arguments to given parser.

        protected (visible only in this module).
        """

        # argument names
        names = list()
        for name in self._names:
            argument_flagments = list(argument_prefixes) + [name]
            names.append('--{}'.format('-'.join(argument_flagments)))

        # dest
        dest = get_child_dest_str(parent_dists) + self._dest

        # keyword arguments for parser
        parser_kwargs = {key: val for key, val in self._kwargs.items()}
        if self._default is not None:
            parser_kwargs['default'] = self._default
        parser_kwargs['type'] = self._type
        if self._action is not None:
            parser_kwargs['action'] = self._action
        parser_kwargs['help'] = self._help
        parser_kwargs['dest'] = dest
        parser_kwargs['metavar'] = self._metavar

        # propagate check
        propagate_state: PropagateState
        propagated_from: Optional[str] = None
        # if at least one name is in propagate_args, then use it
        # (not add a new argument to the parser)
        if any([name in propagate_data for name in self._names]):
            propagate_state = PropagateState.Propagated
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
            argument_target.add_argument(*names, **parser_kwargs)

            # return propagate states
            if self._propagate is None:
                # child parsers cannot have the same argument
                propagate_state = PropagateState.Prohibit
            elif self._propagate:
                # explicitly propagate to child parsers
                propagate_state = PropagateState.ForPropagate
            else:
                # no registration; child parsers can have the same argument without any warnings
                propagate_state = PropagateState.Nothing
        return _AddArgumentReturn(state=propagate_state, targets=self._propagate_targets,
                                  dest=dest, propagated_from=propagated_from)

    def _pr_to_propagatable(self) -> None:
        if self._propagate is not None and not self._propagate:
            raise argparse.ArgumentTypeError('do not specify propagate=False '
                                             'to propagate_arg. ')
        self._propagate = True
