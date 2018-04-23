from hiargparse import ArgumentParser, Namespace

# just same as example.py
from example import Son


if __name__ == '__main__':
    # Make a instance of Son, which has hiargparse.ArgsProvider,
    # without any program arguments.
    # This example is especially useful when you distribute your hi-argparsed program
    # and someone want to use your program without any accessing to his program arguments.

    # first of all, once try print() and you'll see the all parameters
    # (of cource this is not necessary)
    parser = ArgumentParser()
    Son.get_args_provider().add_arguments(parser)
    print(parser.parse_args(args=[]))  # calling with args=[] passes no arguments to the parser

    # then here we go
    son_params = Namespace(
        dict(
            hoge=42, huga='hey', piyo=0.90,
            GS=dict(
                huga='hey', piyo=0.91
            )
        )
    )
    son = Son(son_params)

    # tired to write propagate args (like huga='hey')
    # or values you want to leave default (like hoge=42) ?
    # tell your args_provider to propagate args :)
    args_provider = Son.get_args_provider()
    parser = ArgumentParser()
    args_provider.add_arguments(parser)
    son_params = parser.get_default_parameters()  # get default parameters
    son_params._update(
        dict(
            huga='hey', piyo=0.90,
            GS=dict(
                piyo=0.91
            )
        )
    )
    args_provider.apply_propagations(son_params)  # apply argument propagations
    son = Son(son_params)
