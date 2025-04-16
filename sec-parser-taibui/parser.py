from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import os
import json
from enum import Enum, auto
import warnings
import re

# Suppress XML parsing warning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

class ElementType(Enum):
    """Semantic element types based on sec-parser-external approach"""
    DOCUMENT = auto()
    SECTION_TITLE = auto()
    PARAGRAPH = auto()
    TABLE = auto()
    TABLE_ROW = auto()
    TABLE_CELL = auto()
    LIST = auto()
    LIST_ITEM = auto()
    TEXT = auto()
    SUPPLEMENTARY_TEXT = auto()
    CONTAINER = auto()

@dataclass
class SemanticElement:
    """Enhanced semantic element with more metadata and structure"""
    element_type: ElementType
    text: str
    level: int
    confidence: float
    children: List['SemanticElement']

    def __init__(self, element_type: ElementType, text: str = "", level: int = 0, confidence: float = 1.0):
        self.element_type = element_type
        self.text = text
        self.level = level
        self.confidence = confidence
        self.children = []

    def add_child(self, child: 'SemanticElement') -> None:
        """Add a child element to this element."""
        child.level = self.level + 1
        self.children.append(child)

    def to_dict(self, for_llm: bool = False) -> Dict[str, Any]:
        """Convert the element and its children to a dictionary structure.
        
        Args:
            for_llm: If True, uses abbreviated keys for LLM optimization.
                    If False, uses full parameter names for human readability.
        """
        if for_llm:
            result = {
                't': self.element_type.name,  # type
                'c': self.text,  # content
                'l': self.level  # level
            }
            if self.children:
                result['ch'] = [child.to_dict(for_llm=True) for child in self.children]  # children
        else:
            result = {
                'type': self.element_type.name,
                'content': self.text,
                'level': self.level,
                'confidence': self.confidence
            }
            if self.children:
                result['children'] = [child.to_dict(for_llm=False) for child in self.children]
            
        return result

    def count_elements(self) -> Dict[str, int]:
        """Count the number of each type of element in the tree."""
        counts = {self.element_type.name: 1}
        for child in self.children:
            child_counts = child.count_elements()
            for element_type, count in child_counts.items():
                counts[element_type] = counts.get(element_type, 0) + count
        return counts

class EnhancedSECParser:
    """Enhanced SEC document parser with semantic segmentation approach"""
    
    def __init__(self):
        self.root = SemanticElement(ElementType.DOCUMENT)
        
    def parse_file(self, file_path: str) -> SemanticElement:
        """Parse an HTML file and return the semantic tree."""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return self.parse_html(html_content)
    
    def parse_html(self, html_content: str) -> SemanticElement:
        """Parse HTML content and create semantic elements with enhanced segmentation."""
        soup = BeautifulSoup(html_content, 'html5lib')
        root = SemanticElement(ElementType.DOCUMENT)
        self._process_element(soup, root)
        return root
    
    def _process_element(self, element, parent: SemanticElement) -> None:
        """Enhanced element processing with semantic segmentation."""
        # Skip script and style tags
        if element.name in ['script', 'style']:
            return
            
        # Process text nodes with semantic classification
        if element.string and element.string.strip():
            text = element.string.strip()
            if text:
                element_type, confidence = self._classify_text(text)
                semantic_element = SemanticElement(
                    element_type=element_type,
                    text=text,
                    level=parent.level + 1,
                    confidence=confidence
                )
                parent.add_child(semantic_element)
        
        # Process tables with enhanced structure
        if element.name == 'table':
            table_element = SemanticElement(
                element_type=ElementType.TABLE,
                text='table',
                level=parent.level + 1,
                confidence=0.95
            )
            parent.add_child(table_element)
            self._process_table(element, table_element)
            return
        
        # Process other elements with semantic classification
        for child in element.children:
            if child.name:
                element_type, confidence = self._classify_element(child)
                semantic_element = SemanticElement(
                    element_type=element_type,
                    text=child.name,
                    level=parent.level + 1,
                    confidence=confidence
                )
                parent.add_child(semantic_element)
                self._process_element(child, semantic_element)
    
    def _process_table(self, table, parent: SemanticElement) -> None:
        """Enhanced table processing with semantic structure."""
        for row in table.find_all('tr'):
            row_element = SemanticElement(
                element_type=ElementType.TABLE_ROW,
                text='tr',
                level=parent.level + 1,
                confidence=0.95
            )
            parent.add_child(row_element)
            
            for cell in row.find_all(['td', 'th']):
                cell_type = ElementType.TABLE_CELL
                cell_text = cell.get_text(strip=True)
                cell_element = SemanticElement(
                    element_type=cell_type,
                    text=cell_text,
                    level=parent.level + 1,
                    confidence=0.95
                )
                row_element.add_child(cell_element)
    
    def _classify_element(self, element) -> tuple[ElementType, float]:
        """Enhanced element classification with confidence scores."""
        # Check for SEC-specific patterns first
        if element.name == 'span':
            style = element.get('style', '')
            text = element.get_text(strip=True)
            
            # Check for Item headers (e.g., "Item 4.01")
            if text.startswith('Item') and 'font-weight:700' in style:
                return ElementType.SECTION_TITLE, 0.95
            
            # Check for subheaders (e.g., "(a) Dismissal...")
            if text.startswith(('(a)', '(b)', '(c)', '(d)')) and 'text-decoration:underline' in style:
                return ElementType.SECTION_TITLE, 0.9
        
        # Original HTML tag-based classification
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return ElementType.SECTION_TITLE, 0.95
        elif element.name == 'p':
            return ElementType.PARAGRAPH, 0.9
        elif element.name == 'table':
            return ElementType.TABLE, 0.95
        elif element.name in ['ul', 'ol']:
            return ElementType.LIST, 0.9
        elif element.name == 'li':
            return ElementType.LIST_ITEM, 0.9
        else:
            return ElementType.CONTAINER, 0.8
    
    def _classify_text(self, text: str) -> tuple[ElementType, float]:
        """Enhanced text classification with semantic rules."""
        # Clean the text first
        text = text.strip()
        
        # Check for Item headers (e.g., "Item 4.01")
        if text.startswith('Item'):
            return ElementType.SECTION_TITLE, 0.95
        
        # Enhanced subheader detection
        if self._is_subheader(text):
            return ElementType.SECTION_TITLE, 0.9
        
        # Original text classification rules
        if text.startswith(('Note', 'See accompanying', 'See Note')):
            return ElementType.SUPPLEMENTARY_TEXT, 0.9
        elif len(text) < 50 and text.isupper():
            return ElementType.SECTION_TITLE, 0.85
        else:
            return ElementType.TEXT, 0.8

    def _is_subheader(self, text: str) -> tuple[ElementType, float]:
        """Determine if text is likely a subheader based on basic structural characteristics."""
        # Clean the text
        text = text.strip()
        
        # Skip empty text
        if not text:
            return False
            
        # 1. Check for letter/number patterns (high confidence)
        subheader_patterns = [
            # Letter in parentheses followed by text
            r'^\([a-z]\)\s+[A-Z]',
            # Number in parentheses followed by text
            r'^\(\d+\)\s+[A-Z]',
            # Roman numeral in parentheses followed by text
            r'^\([ivx]+\)\s+[A-Z]',
            # Letter followed by period and text
            r'^[a-z]\.\s+[A-Z]',
            # Number followed by period and text
            r'^\d+\.\s+[A-Z]'
        ]
        
        # Check if text matches any subheader pattern
        for pattern in subheader_patterns:
            if re.match(pattern, text):
                return ElementType.SECTION_TITLE, 0.95
        
        # 2. Basic structural characteristics
        words = text.split()
        
        # Check if text is short (subheaders are typically 1-3 lines)
        if len(words) <= 10:  # Adjust this threshold as needed
            # Check if text starts with capital letter (typical for subheaders)
            if text[0].isupper():
                return ElementType.SECTION_TITLE, 0.9
        
        return ElementType.TEXT, 0.8

def process_documents(input_dir: str, output_dir: str) -> None:
    """Process all HTML files in the input directory and save enhanced JSON output."""
    parser = EnhancedSECParser()
    
    # Create output directories if they don't exist
    human_output_dir = os.path.join(output_dir, 'human_output')
    llm_output_dir = os.path.join(output_dir, 'llm_output')
    os.makedirs(human_output_dir, exist_ok=True)
    os.makedirs(llm_output_dir, exist_ok=True)
    
    # Process all HTML files
    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(input_dir, filename)
            print(f"\nProcessing {filename}...")
            
            # Parse the document
            semantic_tree = parser.parse_file(file_path)
            
            # Save human-readable JSON
            human_output_file = os.path.join(human_output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(human_output_file, 'w', encoding='utf-8') as f:
                json.dump(semantic_tree.to_dict(for_llm=False), f, indent=2, ensure_ascii=False)
            print(f"Human-readable structure saved to: {human_output_file}")
            
            # Save LLM-optimized JSON
            llm_output_file = os.path.join(llm_output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(llm_output_file, 'w', encoding='utf-8') as f:
                json.dump(semantic_tree.to_dict(for_llm=True), f, indent=None, separators=(',', ':'), ensure_ascii=False)
            print(f"LLM-optimized structure saved to: {llm_output_file}")

if __name__ == "__main__":
    input_dir = "downloaded_html"
    output_dir = "enhanced_output"
    process_documents(input_dir, output_dir) 
