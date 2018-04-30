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
