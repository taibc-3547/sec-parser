from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import os
import json
from enum import Enum, auto
import warnings

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
    attributes: Dict[str, Any]
    children: List['SemanticElement']
    parent: Optional['SemanticElement']
    level: int
    confidence: float  # Confidence score for semantic classification
    metadata: Dict[str, Any]  # Additional metadata like position, formatting, etc.

    def __init__(self, element_type: ElementType, text: str = "", attributes: Dict[str, Any] = None, confidence: float = 1.0):
        self.element_type = element_type
        self.text = text
        self.attributes = attributes or {}
        self.children = []
        self.parent = None
        self.level = 0
        self.confidence = confidence
        self.metadata = {}

    def add_child(self, child: 'SemanticElement') -> None:
        """Add a child element to this element."""
        child.parent = self
        child.level = self.level + 1
        self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the element and its children to a dictionary with enhanced structure."""
        return {
            'type': self.element_type.name,
            'text': self.text,
            'attributes': self.attributes,
            'level': self.level,
            'confidence': self.confidence,
            'metadata': self.metadata,
            'children': [child.to_dict() for child in self.children]
        }

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
        self._process_element(soup, self.root)
        return self.root
    
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
                    attributes={'tag': element.name},
                    confidence=confidence
                )
                parent.add_child(semantic_element)
        
        # Process tables with enhanced structure
        if element.name == 'table':
            table_element = SemanticElement(
                element_type=ElementType.TABLE,
                attributes={'tag': 'table'},
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
                    attributes={'tag': child.name},
                    confidence=confidence
                )
                parent.add_child(semantic_element)
                self._process_element(child, semantic_element)
    
    def _process_table(self, table, parent: SemanticElement) -> None:
        """Enhanced table processing with semantic structure."""
        for row in table.find_all('tr'):
            row_element = SemanticElement(
                element_type=ElementType.TABLE_ROW,
                attributes={'tag': 'tr'}
            )
            parent.add_child(row_element)
            
            for cell in row.find_all(['td', 'th']):
                cell_type = ElementType.TABLE_CELL
                cell_text = cell.get_text(strip=True)
                cell_element = SemanticElement(
                    element_type=cell_type,
                    text=cell_text,
                    attributes={'tag': cell.name}
                )
                row_element.add_child(cell_element)
    
    def _classify_element(self, element) -> tuple[ElementType, float]:
        """Enhanced element classification with confidence scores."""
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
        # Simple rules for text classification
        if text.startswith(('Note', 'See accompanying', 'See Note')):
            return ElementType.SUPPLEMENTARY_TEXT, 0.9
        elif len(text) < 50 and text.isupper():
            return ElementType.SECTION_TITLE, 0.85
        else:
            return ElementType.TEXT, 0.8

def process_documents(input_dir: str, output_dir: str) -> None:
    """Process all HTML files in the input directory and save enhanced JSON output."""
    parser = EnhancedSECParser()
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all HTML files
    for filename in os.listdir(input_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(input_dir, filename)
            print(f"\nProcessing {filename}...")
            
            # Parse the document
            semantic_tree = parser.parse_file(file_path)
            
            # Save enhanced structure to JSON file
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(semantic_tree.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"Enhanced structure saved to: {output_file}")

if __name__ == "__main__":
    input_dir = "downloaded_html"
    output_dir = "enhanced_output"
    process_documents(input_dir, output_dir) 