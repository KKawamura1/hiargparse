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
    son_params = Namespace(dict(
        hoge=10, huga='hey', piyo=0.90,
        GS=Namespace(dict(
            huga='hey', piyo=0.91
        ))
    ))
    son = Son(son_params)

    # tired to write propagate args (like huga='hey') many times?
    # an argument parser also accepts dict input
    parser = ArgumentParser()
    Son.get_args_provider().add_arguments(parser)
    son_params = parser.parse_args_from_dict(dict(
        hoge=10, huga='hey', piyo=0.90,
        GS=Namespace(dict(
            huga='hey', piyo=0.91
        ))
    ))
    son = Son(son_params)
