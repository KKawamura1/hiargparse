import argparse
from hiargparse import ArgumentParser, Namespace
from hiargparse import ArgsProvider, Arg, ChildProvider


class Tire:
    @classmethod
    def get_args_provider(cls) -> ArgsProvider:
        return ArgsProvider(
            args=[
                Arg('radius', 21.0),
                Arg('unit-of-radius', 'cm', choices=['cm', 'm', 'mm']),
                Arg('for-winter', action='store_true')
            ]
        )

    def __init__(self, params: Namespace) -> None:
        repr_str = 'Tire. rad: {} {}. '.format(params.radius, params.unit_of_radius)
        if params.for_winter:
            repr_str += 'For winter. '
        else:
            repr_str += 'NOT for winter. '
        print(repr_str)


if __name__ == '__main__':
    # set a root argument provider (same as other argument providers)
    args_provider = ArgsProvider(
        args=[Arg('foo', 'bar')],
        child_providers=[ChildProvider(Tire)]
    )

    # quite usual argparse way except *new code* line
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')
    args_provider.add_arguments(parser)  # *new code*
    params = parser.parse_args()

    # now you have ALL parameters including child and grandchild arguments
    # please try to execute with --help
    print(params.foo)
    tire = Tire(params._get_child('Tire'))
