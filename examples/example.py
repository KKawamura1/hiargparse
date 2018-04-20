from hiargparse import ArgumentParser, Namespace  # just same as argparse
from hiargparse import ArgsProvider, Arg, ChildProvider  # need to define child arguments


class GrandSon:
    @classmethod
    def get_args_provider(cls) -> ArgsProvider:
        return ArgsProvider(
            args=[
                Arg('huga', None, type=str),
                Arg('piyo', 0.99, help='%(default-text)s This argument is Piyopiyo.')
            ]
        )

    def __init__(self, params: Namespace) -> None:
        print(params.huga, params.piyo)


class Son:
    @classmethod
    def get_args_provider(cls) -> ArgsProvider:
        return ArgsProvider(
            args=[
                Arg('hoge', 42),
                Arg('piyo', 0.95, propagate=False)
            ],
            propagate_args=[
                Arg('huga', None, type=str)
            ],
            child_providers=[
                ChildProvider(GrandSon, dest='GS')
            ]
        )

    def __init__(self, params: Namespace) -> None:
        print(params.hoge, params.huga, params.piyo)
        gson = GrandSon(params._get_child('GS'))


if __name__ == '__main__':
    # set a root argument provider (same as other argument providers)
    args_provider = ArgsProvider(
        args=[Arg('foo', 'bar')],
        child_providers=[ChildProvider(Son)]
    )

    # quite usual argparse way except *new code* line
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')
    args_provider.add_arguments(parser)  # *new code*
    params = parser.parse_args()

    # now you have ALL parameters including child and grandchild arguments
    # please try to execute with --help
    print(params.foo)
    son = Son(params._get_child('Son'))
