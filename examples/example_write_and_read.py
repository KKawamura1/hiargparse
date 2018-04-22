from hiargparse import ArgumentParser, Namespace
from hiargparse import ArgsProvider, Arg, ChildProvider, ConfigureFileType
from example import Son
from typing import Optional
from pathlib import Path
from sys import exit


if __name__ == '__main__':
    # set a root argument provider
    args_provider = ArgsProvider(
        args=[
            Arg('write-to', type=Path),
            Arg('read-from', type=Path),
            Arg('file-type', default='json', choices=['json'])
        ],
        child_providers=[ChildProvider(Son)]
    )

    # parse arguments as usual
    parser = ArgumentParser()
    args_provider.add_arguments(parser)
    params = parser.parse_args()

    write_to: Optional[Path] = params.write_to
    read_from: Optional[Path] = params.read_from
    file_type: ConfigureFileType = dict(json=ConfigureFileType.json)[params.file_type]
    if write_to is not None:
        # write configure arguments to the given file
        args_provider.write_configure_arguments(path=write_to, file_type=file_type)
        exit()
    if read_from is not None:
        # read configure arguments from the given file
        read_params = args_provider.read_configure_arguments(path=read_from)
        params._update(read_params)

    # now you have ALL parameters including child and grandchild arguments
    # please execute with --write-to FILE_PATH
    son = Son(params.Son)
