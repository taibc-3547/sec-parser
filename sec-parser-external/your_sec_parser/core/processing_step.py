from abc import ABC, abstractmethod
from typing import List
from ..elements.abstract_semantic_element import AbstractSemanticElement

class AbstractProcessingStep(ABC):
    @abstractmethod
    def process(self, elements: List[AbstractSemanticElement]) -> List[AbstractSemanticElement]:
        raise NotImplementedError 