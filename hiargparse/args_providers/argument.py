import argparse
import enum
import warnings
from typing import Union, Sequence, Collection, Optional, Callable, TypeVar, NamedTuple
from typing import Dict, List, Any, Type
from hiargparse.hierarchy import parents_and_key_to_long_key, format_parent_names_and_key
from hiargparse.file_protocols.dict_writers import AbstractDictWriter
from hiargparse.miscs import DirtyAccessToArgparse
from .exceptions import ArgumentError, ConflictWarning, PropagationError


ArgumentAccepter = Union[argparse.ArgumentParser, DirtyAccessToArgparse.ArgumentGroup]


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


ValueT = TypeVar('ValueT')
StrToValueT = Callable[[str], ValueT]


class Arg:
    """An argument to be registered to ArgsProvider.

    Take all arguments that argparse.add_argument() can receive.
    Args:
        main_name: used in a default value for several arguments and its signature.
        propagate: If True, then propagate its value to all child Args
                   that have the same name.
                   If False, no propagation is occurred and the same-name Arg
                   is treated as a totally different Arg.
        propagate_targets: names that used in checking whether the target is
                   the same (occur propagation) or not.

    methods started with _pr_ is used in other classes in this module,
    but invisible from outside of this module.
    """

    def __init__(
            self,
            name: Union[str, Sequence[str]],
            default: Optional[ValueT] = None,
            *,
            main_name: str = None,
            type: Union[StrToValueT, Type[StrToValueT]] = None,
            dest: str = None,
            metavar: Union[str, Sequence[str]] = None,
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
            raise ArgumentError('At least one name must be given.')
        # main_name
        if main_name is None:
            main_name = names[0]
        # default, type
        if type is None and default is not None:
            type = default.__class__
        # dest
        if dest is None:
            dest = main_name.replace('-', '_')
        # propagate targets
        if propagate_targets is None:
            propagate_targets = names
        # metavar
        if metavar is None:
            metavar = main_name.upper()
        if not isinstance(metavar, str):
            # sequence to tuple
            metavar = tuple(metavar)

        self._main_name = main_name
        self._names = names
        self._default = default
        self._type = type
        self._dest = dest
        self._metavar = metavar
        self._propagate = propagate
        self._propagate_targets = list(propagate_targets)
        self._kwargs = kwargs

    @property
    def main_name(self) -> str:
        return self._main_name

    @property
    def dest(self) -> str:
        return self._dest

    def _pr_add_argument(
            self,
            argument_target: ArgumentAccepter,
            writer: AbstractDictWriter,
            parent_names: List[str],
            parent_dists: List[str],
            argument_prefixes: List[str],
            propagate_data: Dict[str, str],
            prohibited_args: Dict[str, str],
    ) -> _AddArgumentReturn:
        """add arguments to given parser.

        protected (visible only in this module).
        """

        # argument names
        names = []
        for name in self._names:
            argument_flagments = list(argument_prefixes) + [name]
            names.append('--{}'.format('-'.join(argument_flagments)))

        # dest
        dest = parents_and_key_to_long_key(parent_dists, self._dest)

        # keyword arguments for parser
        parser_kwargs = {key: val for key, val in self._kwargs.items()}
        parser_kwargs.update(dest=dest, metavar=self._metavar)
        if self._type is not None:
            parser_kwargs['type'] = self._type
        if self._default is not None:
            parser_kwargs['default'] = self._default

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
                # if not 1, it must be >= 2
                assert propagated_from_set
                # propagation error; abort
                multi_propagated_arg = format_parent_names_and_key(parent_names, self._main_name)
                raise PropagationError(
                    ('argument {} ([{}]) has more than 1 deferent propagation. '
                     ).format(multi_propagated_arg, ', '.join(self._names))
                )
            propagated_from = list(propagated_from_set)[0]
        else:
            if any([name in prohibited_args for name in self._names]):
                # if at least one name is in prohibited_args, then warn it
                conflict_name, conflict_with = [(name, prohibited_args[name])
                                                for name in self._names
                                                if name in prohibited_args][0]
                conflict_arg = format_parent_names_and_key(parent_names, conflict_name)
                warning_message = (
                    'argument {} has name conflicts with argument {}; '
                    'please specify propagate=False if this conflict is '
                    'your desirable operation. '
                ).format(conflict_arg, conflict_with)
                warnings.warn(ConflictWarning(warning_message))
            # add the argument
            action: argparse.Action
            # some actions do not take some arguments
            try:
                # the stub file does not know, but I know
                # that add_argument really returns the action
                action = argument_target.add_argument(*names, **parser_kwargs)  # type: ignore
            except TypeError:
                del parser_kwargs['metavar']
                action = argument_target.add_argument(*names, **parser_kwargs)  # type: ignore

            # replacing help text
            default_help_text = '{}. '.format(self._main_name)
            if len(self._names) >= 2:
                default_help_text += '(a.k.a. {}) '.format(', '.join(self._names[1:]))
            # if type is easy-to-understand one, then show it
            if action.type in [bool, int, float, complex, str]:
                default_help_text += 'type: %(type)s. '
            # default
            if action.default is not None:
                default_help_text += 'default: %(default)s. '
            # nargs
            if action.nargs == 0 and action.const is not None:
                default_help_text += 'Use this argument to set {}. '.format(action.const)
            elif isinstance(action.nargs, int) and action.nargs >= 2:
                default_help_text += 'Please specify exactry {} arguments. '.format(action.nargs)
            # choices
            if action.choices is not None:
                default_help_text += 'Choose from: %(choices)s. '
            # set help text
            if action.help is None:
                action.help = default_help_text
            else:
                action.help = action.help.replace('%(default-text)s', default_help_text)

            # write about the argument
            writer.add_argument(action, dest=self._names[0], comment_outs=True)

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
        """Turn on its propagate property"""
        if self._propagate is not None and not self._propagate:
            raise ArgumentError('do not specify propagate=False to propagate_arg. ')
        self._propagate = True
