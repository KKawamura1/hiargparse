from .abstract_dict_reader import AbstractDictReader
from typing import Dict, Any
import importlib.util
from .normalize_dict import normalize_dict
from .added_double_hyphen import added_double_hyphen

# deferred erroring for yaml package
# (to work correctly without yaml if you don't use yaml at all)
if importlib.util.find_spec(name='yaml') is None:
    _yaml_exist = False
else:
    import yaml
    _yaml_exist = True


class YAMLReader(AbstractDictReader):
    def __init__(self) -> None:
        if not _yaml_exist:
            # abort
            try:
                # force raise ImportError
                import yaml  # noqa: F401,F811
            except ImportError as exc:
                additional_message = (': this error happens because {} want to use it.'
                                      .format(type(self).__name__))
                raise type(exc)(str(exc) + additional_message) from exc

    def to_normalized_dict(self, input_documents: str) -> Dict[str, Any]:
        nested = self._to_nested_dict(input_documents)
        target: Dict[str, Any] = dict()
        normalize_dict(nested, target, '')
        return added_double_hyphen(target)

    def _to_nested_dict(self, input_documents: str) -> Dict[str, Any]:
        return yaml.safe_load(input_documents)
