from ..core.processing_step import AbstractProcessingStep
from ..elements.title_element import TitleElement

class TitleClassifier(AbstractProcessingStep):
    def process(self, elements):
        for i, element in enumerate(elements):
            if element._html_tag.name.startswith('h'):
                level = int(element._html_tag.name[1]) if len(element._html_tag.name) > 1 else 1
                elements[i] = TitleElement(element._html_tag, level=level)
        return elements 