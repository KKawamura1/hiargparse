from hiargparse import ArgumentParser, Namespace
from hiargparse import ArgsProvider, Arg, ChildProvider, ConfigureFileType
from example import Son

import argparse
from typing import Optional, Any
from pathlib import Path
from sys import exit


# write file action
class WriteToFileAction(argparse.Action):
    def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: Any,
            option_string: str = None
    ) -> None:
        assert isinstance(parser, ArgumentParser)
        assert isinstance(namespace, Namespace)
        assert isinstance(values, Path)
        assert 'file_type' in namespace and namespace.file_type is not None
        # write configure arguments to the given file as the given type
        file_type = ConfigureFileType[namespace.file_type]
        parser.write_configure_arguments(path=values, file_type=file_type)
        # when you want to write out a configure file,
        # usually you want to stop this program, fill in your brand-new configure file,
        # and then restart it, so I'll exit
        exit()


# read file action
class ReadFromFileAction(argparse.Action):
    def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: Any,
            option_string: str = None
    ) -> None:
        assert isinstance(parser, ArgumentParser)
        assert isinstance(namespace, Namespace)
        assert isinstance(values, Path)
        # read configure arguments from the given file
        new_params = parser.read_configure_arguments(path=values)
        namespace._update(new_params)


if __name__ == '__main__':
    # set a root argument provider
    file_type_names = [file_type.name for file_type in ConfigureFileType]
    args_provider = ArgsProvider(
        args=[
            Arg('file-type', default='json', choices=file_type_names),
            # write-to argument
            Arg('write-to', type=Path, action=WriteToFileAction,
                help='%(default-text)s Write a configure file in the given path and exit. '),
            # read-from argument
            Arg('read-from', type=Path, action=ReadFromFileAction,
                help='%(default-text)s Read from the given configure file. '),
        ],
        child_providers=[ChildProvider(Son)]
    )

    # parse arguments as usual
    parser = ArgumentParser()
    parser.add_argument('-V', '--version', action='version', version='v1.0')
    parser.add_arguments_from_provider(args_provider)
    params = parser.parse_args()

    # now you have ALL parameters including child and grandchild arguments
    # please execute with --write-to FILE_PATH
    son = Son(params.Son)
