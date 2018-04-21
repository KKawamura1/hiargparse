import argparse
from hiargparse import ArgumentParser, Namespace
from hiargparse import ArgsProvider, Arg, ChildProvider


class Tire:
    @classmethod
    def get_args_provider(cls) -> ArgsProvider:
        return ArgsProvider(
            args=[
                # type can be specified; if not, default.__class__ is used
                Arg('radius', 21, type=float),
                # choices
                Arg('unit-of-radius', 'cm', choices=['cm', 'm', 'mm']),
                # store_true action
                Arg('for-winter', action='store_true'),
                # multiple names
                Arg(['style', 'type'], 'cool')
            ]
        )

    def __init__(self, params: Namespace) -> None:
        # Namespace is accessable with getattr
        self._radius = params.radius
        # also getitem is supported (note that argparse.Namespace does not support this)
        self._radius_unit = params['unit_of_radius']
        # Namespace does not memorize its type, so variable type annotation is recommended
        self._for_winter: bool = params.for_winter

    def __repr__(self) -> str:
        if self._for_winter:
            winter_str = 'for winter'
        else:
            winter_str = 'NOT for winter'
        repr_str = '<Tire of rad: {} {} ({}) >'.format(self._radius, self._radius_unit, winter_str)
        return repr_str


class Car:
    @classmethod
    def get_args_provider(cls) -> ArgsProvider:
        return ArgsProvider(
            args=[
                Arg('radius', 21.0)
            ],
            # args propagation
            # the user can specify only the root argument
            # and its value is propagated to all child providers
            propagate_args=[
                Arg('unit_of_radius', 'cm', choices=['cm', 'm', 'mm']),
                # you can use a different name from the propagation-target name
                Arg('for-winter-car', action='store_true', propagate_targets=['for-winter'])
            ],
            child_providers=[
                # multiple providers for a class
                ChildProvider(cls=Tire, name='front_tire', prefix='ftire',
                              # you can choose not to provide some arg
                              # to serve it at runtime (ex. in __init__())
                              no_provides={'radius'}),
                ChildProvider(cls=Tire, name='back_tire', prefix='btire',
                              no_provides={'radius'})
            ]
        )

    def __init__(self, params: Namespace) -> None:
        # some additional (not from arguments) parameters
        front_tire_params = params._get_child('front_tire')._replace(radius=params.radius)
        # multiple instances for a providers
        self._front_tires = [Tire(front_tire_params) for i in range(2)]
        # Namespace has some useful attributes; _replace, _update, _asdict, and more.
        back_tire_params = params._get_child('back_tire')._update({'radius': params.radius + 1.0})
        self._back_tires = [Tire(back_tire_params) for i in range(2)]

    def print_spec(self) -> None:
        print('Car: ')
        print('front tires: {}'.format(', '.join([str(tire) for tire in self._front_tires])))
        print('back tires: {}'.format(', '.join([str(tire) for tire in self._back_tires])))


if __name__ == '__main__':
    # set a root argument provider (same as other argument providers)
    args_provider = ArgsProvider(
        child_providers=[ChildProvider(Car)]
    )

    # quite usual argparse way except *new code* line
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')
    args_provider.add_arguments(parser)  # *new code*
    params = parser.parse_args()

    # now you have ALL parameters including child and grandchild arguments
    # please try to execute with --help
    car = Car(params._get_child('Car'))
    car.print_spec()
