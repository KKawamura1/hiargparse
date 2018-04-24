from abc import ABC, abstractmethod
from typing import Dict, Any


class AbstractDictReader(ABC):
    @abstractmethod
    def to_normalized_dict(self, input_documents: str) -> Dict[str, Any]:
        raise NotImplementedError()
