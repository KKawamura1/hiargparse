from hiargparse import ArgumentParser, Namespace
from hiargparse import ArgsProvider, Arg, ChildProvider, ConfigureFileType
from example import Son
from complicated_example import Car

import argparse
from typing import Optional, Any
from pathlib import Path
from sys import exit


if __name__ == '__main__':
    # set a root argument provider
    file_type_names = [file_type.name for file_type in ConfigureFileType]

    args_provider = ArgsProvider(
        args=[
            Arg('file-type', default='toml', choices=file_type_names),
            # write-to argument
            Arg('write-to', type=Path,
                help='%(default-text)s Write a configure file in the given path and exit. '),
            # read-from argument
            Arg('read-from', type=Path,
                help='%(default-text)s Read from the given configure file. '),
        ],
        child_providers=[ChildProvider(Son)]
    )

    # parse arguments as usual
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')
    parser.add_arguments_from_provider(args_provider)
    params = parser.parse_args()

    # write to / read from a file
    file_type = ConfigureFileType[params.file_type]
    if params.write_to is not None:
        path_w: Path = params.write_to
        # write configure arguments to the given file as the given type
        with path_w.open('w') as f:
            f.write(args_provider.write_out_configure_arguments(file_type))
        # when you want to write out a configure file,
        # usually you want to stop this program, fill in your brand-new configure file,
        # and then restart it, so I'll exit
        exit()
    if params.read_from is not None:
        path_r: Path = params.read_from
        # read configure arguments from the given file
        with path_r.open('r') as f:
            read_params = args_provider.read_configure_arguments(f.read(), file_type)

        # Usually you want to overwrite the parameters from the file
        # with the parameters from program arguments.
        # Namely, your desirable priority would be
        # (higher)
        # 1. program arguments
        # 2. arguments written in the config file
        # 3. default values
        # (lower)
        # then you can simply overwrite read_params with reloading arguments
        params = parser.parse_args(namespace=read_params)

    print(params)
    # please execute with --write-to / --read-from FILE_PATH
    son = Son(params.Son)
