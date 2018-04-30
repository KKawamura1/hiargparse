Hierarchical Argparse
====

Hiargparse is a hierarchical and highly sophisticated variant of [argparse](https://docs.python.org/3/library/argparse.html).

## Minimal Code
```python
from hiargparse import ArgsProvider, Arg, ChildProvider, ArgumentParser

child = ArgsProvider(
    args=[Arg('baz', default=42)]
)
root = ArgsProvider(
    args=[Arg('foo', default='bar')],
    child_providers=[ChildProvider(provider=child, name='child')]
)
parser = ArgumentParser()
parser.add_arguments_from_provider(root)
print(parser.parse_args())
```

## Description

Hiargparse automatically generates the command-line arguments with your all classes in your tree-like module structures with minimal codings.

Suppose you make a large module, and your hierarchically deep class, say `foo.bar.baz.ham.spam.Egg`, requires some arguments, say `heights` and `widths`.
`Foo` makes an instance of `Bar`, `Bar` makes an instance of `Baz`, ..., and `Spam` makes an `Egg` which has the two arguments.
When you want to pass them command-line options, you have to write the two, `heights` and `widths`, in the constructor of `Foo`, `Bar`, ..., and `Spam`.
What if the `Egg` is updated and wants to require some new arguments, like `depth` or `length`?
Hiargparse passes the arguments directly to the classes without any black magics.

## Features

With this module, you can

- easily make hierarchical (tree-like) command-line arguments with [argparse](https://docs.python.org/3/library/argparse.html)
 - Each argument is automatically help-texted and grouped into `argparse.ArgumentGroup`.
- get a more useful Namespace object than the original
 - Accessing with dict-like key, getting the child Namespace, converting to/from dictionaries, and so on
- write/read the arguments to/from  some configure files with well known formats
 - Currently we supports [yaml](http://yaml.org/) and [toml](https://github.com/toml-lang/toml).

Also, this module

- is almost compatible with original argparse; you can gradually introduce it to your large projects.
- works without command-line arguments; when you distribute your module with hiargparse,
users still can select whether to feed arguments to it with a command-line or programatic way.

This module is inspired by rlpytorch.args_provider in [FacebookAIResearch/ELF](https://github.com/facebookresearch/ELF).

## Installation

Use `git clone` and set `PYTHONPATH` to make hiargparse found by your python.

(We are trying to register this module to the [PyPI](https://pypi.org), which allows you to simply use `pip install hiargparse`.)

## Requirements

- python >= 3.6.0
- typing_extensions (for typing\_extentions.Protocol in python 3.6) >= 3.6.2.1
- pyyaml >= 3.12 (only if you use yaml write/read)
- toml >= 0.9.4 (only if you use toml write/read)

## Examples

- See `/examples/example.py` to easy start.
- You can use hiargparse with original ArgumentParser. See `/examples/example_with_original.py`.
- If you want to use hiargparse without command-line arguments, see `/examples/example_without_program_arguments.py`.
- `/examples/example_write_and_read.py` describes how to write and read the arguments with a configure file.
- A lot of things you can do with hiargparse are shown in `/examples/complicated_example.py`.

## Contribution

- Any contribution is welcome!
- Fork the repo, create a branch, add your awesome changes, and make a new Pull Request.
- If you find some bugs, please report in issue.

## Author

- Keigo Kawamura (Department of Electrical Engineering and Information Systems (EEIS), Graduate School of Engineering, The University of Tokyo)
 - kkawamura@logos.t.u-tokyo.ac.jp
