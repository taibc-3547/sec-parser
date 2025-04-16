from ..core.processing_step import AbstractProcessingStep
from ..elements.table_element import TableElement
from ..elements.text_element import TextElement

class TableClassifier(AbstractProcessingStep):
    def process(self, elements):
        for i, element in enumerate(elements):
            if element._html_tag.name == 'table':
                elements[i] = TableElement(element._html_tag)
        return elements 