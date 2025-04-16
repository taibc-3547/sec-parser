from abc import ABC
from typing import Any

class AbstractSemanticElement(ABC):
    def __init__(self, html_tag):
        self._html_tag = html_tag
        self.section = None
    
    @property
    def text(self) -> str:
        return self._html_tag.text
    
    def get_summary(self) -> str:
        return self.text
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.__class__.__name__,
            "text": self.text,
            "section": self.section
        } 