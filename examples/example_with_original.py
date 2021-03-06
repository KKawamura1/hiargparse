from argparse import ArgumentParser  # use traditional argparse instead hiargparse
from hiargparse import ArgsProvider, Arg, ChildProvider  # need to define child arguments
from hiargparse import Namespace  # wrapper for argparse.Namespace

# just same as example.py
from example import Son


if __name__ == '__main__':
    # set a root argument provider (same as other argument providers)
    args_provider = ArgsProvider(
        args=[Arg(name='foo', default='bar')],
        child_providers=[ChildProvider(Son)]
    )

    # quite usual argparse way
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')

    # here we have to write some weird code

    # invoke args_provider's method with the parser
    # instead of parser's method with the args_provider
    args_provider.add_arguments_to_parser(parser)

    # parse_args with original parser
    # in a tipical case, this line hides behind other libraries' implementation
    params = parser.parse_args()

    # convert argparse.Namespace to hiargparse.Namespace
    params = Namespace(params)
    # do some deferred actions relating to arg propagation
    args_provider.apply_propagations(params)

    # now you have ALL parameters including child and grandchild arguments
    # please try to execute with --help
    print(params.foo)
    son = Son(params.Son)
    son.print_()
