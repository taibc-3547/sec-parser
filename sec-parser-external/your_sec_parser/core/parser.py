from typing import List
from bs4 import BeautifulSoup
from .html_tag import HtmlTag
from .abstract_semantic_element import AbstractSemanticElement
from .processing_step import AbstractProcessingStep
from ..elements.text_element import TextElement
import re

class SECParser:
    def __init__(self):
        self._steps = self._get_default_steps()
    
    def _get_default_steps(self) -> List[AbstractProcessingStep]:
        from ..processing_steps.table_classifier import TableClassifier
        from ..processing_steps.title_classifier import TitleClassifier
        from ..processing_steps.section_manager import SectionManager
        
        return [
            TableClassifier(),
            TitleClassifier(),
            SectionManager()
        ]
    
    def _extract_html_content(self, filing_content: str) -> str:
        """Extract HTML content from SEC filing text."""
        # SEC filings often contain HTML within the text
        html_start = filing_content.find('<HTML>')
        html_end = filing_content.find('</HTML>')
        
        if html_start != -1 and html_end != -1:
            return filing_content[html_start:html_end + 7]
        
        # If no HTML tags found, try to find the first HTML-like content
        html_match = re.search(r'<[^>]+>', filing_content)
        if html_match:
            return filing_content[html_match.start():]
        
        return filing_content
    
    def parse(self, filing_content: str) -> List[AbstractSemanticElement]:
        """
        Parse SEC filing content into semantic elements.
        
        Args:
            filing_content: Raw content of the SEC filing
            
        Returns:
            List of semantic elements
        """
        # Extract HTML content
        html_content = self._extract_html_content(filing_content)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Convert to semantic elements
        elements = []
        for tag in soup.find_all(['p', 'table', 'h1', 'h2', 'h3', 'div']):
            # Skip empty or whitespace-only tags
            if not tag.get_text(strip=True):
                continue
                
            html_tag = HtmlTag(tag)
            elements.append(TextElement(html_tag))
        
        # Process elements
        for step in self._steps:
            elements = step.process(elements)
        
        return elements 