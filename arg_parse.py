import argparse
from typing import Any, Sequence, Tuple, List


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def parse_known_args(
            self,
            args: Sequence[str] = None,
            namespace: argparse.Namespace = None
    ) -> Tuple[argparse.Namespace, List[str]]:
        """argparse.Namespace to hi_arg_parse.Namespace"""
        if namespace is None:
            namespace = argparse.Namespace()
        return super().parse_known_args(args, namespace)
