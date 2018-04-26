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
        self._params = params

    def print_(self) -> None:
        print(self._params.huga, self._params.piyo)


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
        self._params = params
        self._gson = GrandSon(params.GS)

    def print_(self) -> None:
        print(params.hoge, params.huga, params.piyo)
        self._gson.print_()


if __name__ == '__main__':
    # set a root argument provider (same as other argument providers)
    args_provider = ArgsProvider(
        args=[Arg(name='foo', default='bar')],
        child_providers=[ChildProvider(Son)]
    )

    # quite usual argparse way except *new code* line
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')
    parser.add_arguments_from_provider(args_provider)  # *new code*
    params = parser.parse_args()

    # now you have ALL parameters including child and grandchild arguments
    # please try to execute with --help
    print(params.foo)
    son = Son(params.Son)
    son.print_()
