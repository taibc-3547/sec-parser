from ..core.abstract_semantic_element import AbstractSemanticElement

class TitleElement(AbstractSemanticElement):
    def __init__(self, html_tag, level: int = 1):
        super().__init__(html_tag)
        self.level = level 