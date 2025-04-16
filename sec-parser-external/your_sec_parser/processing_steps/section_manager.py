from ..core.processing_step import AbstractProcessingStep
from ..elements.title_element import TitleElement

class SectionManager(AbstractProcessingStep):
    def process(self, elements):
        current_section = None
        for element in elements:
            if isinstance(element, TitleElement):
                current_section = element.text
            element.section = current_section
        return elements 