from argparse import ArgumentParser  # use traditional argparse instead hiargparse
from hiargparse import ArgsProvider, Arg, ChildProvider  # need to define child arguments
from hiargparse import Namespace  # wrapper for argparse.Namespace

# just same as example.py
from example import Son


if __name__ == '__main__':
    # set a root argument provider (same as other argument providers)
    args_provider = ArgsProvider(
        args=[Arg('foo', 'bar')],
        child_providers=[ChildProvider(Son)]
    )

    # quite usual argparse way
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')

    # same as example.py
    args_provider.add_arguments(parser)
    params = parser.parse_args()

    # here we have to write some weird code
    # cast argparse.Namespace to hiargparse.Namespace
    params = Namespace(params)
    # do some deferred actions relating to arg propagation
    args_provider.apply_deferring_actions(params)
    # normalize params (resolve some trick used in args_provider.add_argument)
    params._normalize()

    # now you have ALL parameters including child and grandchild arguments
    # please try to execute with --help
    print(params.foo)
    son = Son(params._get_child('Son'))
