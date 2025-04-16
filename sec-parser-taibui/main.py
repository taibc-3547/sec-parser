from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import os
import json

@dataclass
class SemanticElement:
    """Represents a semantic element in the document."""
    element_type: str  # e.g., 'section_title', 'paragraph', 'table'
    text: str
    attributes: Dict[str, Any]
    children: List['SemanticElement']
    parent: Optional['SemanticElement']
    level: int  # depth in the tree

    def __init__(self, element_type: str, text: str = "", attributes: Dict[str, Any] = None):
        self.element_type = element_type
        self.text = text
        self.attributes = attributes or {}
        self.children = []
        self.parent = None
        self.level = 0

    def add_child(self, child: 'SemanticElement') -> None:
        """Add a child element to this element."""
        child.parent = self
        child.level = self.level + 1
        self.children.append(child)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the element and its children to a dictionary."""
        return {
            'type': self.element_type,
            'text': self.text,
            'attributes': self.attributes,
            'level': self.level,
            'children': [child.to_dict() for child in self.children]
        }

    def count_elements(self) -> Dict[str, int]:
        """Count the number of each type of element in the tree."""
        counts = {self.element_type: 1}
        for child in self.children:
            child_counts = child.count_elements()
            for element_type, count in child_counts.items():
                counts[element_type] = counts.get(element_type, 0) + count
        return counts

class SECDocumentParser:
    """Parses SEC EDGAR HTML documents into semantic elements."""
    
    def __init__(self):
        self.root = SemanticElement('document')
        
    def parse_file(self, file_path: str) -> SemanticElement:
        """Parse an HTML file and return the semantic tree."""
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return self.parse_html(html_content)
    
    def parse_html(self, html_content: str) -> SemanticElement:
        """Parse HTML content and create semantic elements."""
        soup = BeautifulSoup(html_content, 'html5lib')
        self._process_element(soup, self.root)
        return self.root
    
    def _process_element(self, element, parent: SemanticElement) -> None:
        """Recursively process HTML elements and create semantic elements."""
        # Skip script and style tags
        if element.name in ['script', 'style']:
            return
            
        # Process text nodes
        if element.string and element.string.strip():
            text = element.string.strip()
            if text:
                semantic_element = SemanticElement(
                    element_type='text',
                    text=text,
                    attributes={'tag': element.name}
                )
                parent.add_child(semantic_element)
        
        # Process tables
        if element.name == 'table':
            table_element = SemanticElement(
                element_type='table',
                attributes={'tag': 'table'}
            )
            parent.add_child(table_element)
            self._process_table(element, table_element)
            return
        
        # Process other elements
        for child in element.children:
            if child.name:
                semantic_element = SemanticElement(
                    element_type=self._determine_element_type(child),
                    attributes={'tag': child.name}
                )
                parent.add_child(semantic_element)
                self._process_element(child, semantic_element)
    
    def _process_table(self, table, parent: SemanticElement) -> None:
        """Process table elements and their contents."""
        for row in table.find_all('tr'):
            row_element = SemanticElement(
                element_type='table_row',
                attributes={'tag': 'tr'}
            )
            parent.add_child(row_element)
            
            for cell in row.find_all(['td', 'th']):
                cell_element = SemanticElement(
                    element_type='table_cell',
                    text=cell.get_text(strip=True),
                    attributes={'tag': cell.name}
                )
                row_element.add_child(cell_element)
    
    def _determine_element_type(self, element) -> str:
        """Determine the semantic type of an HTML element."""
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return 'section_title'
        elif element.name == 'p':
            return 'paragraph'
        elif element.name == 'table':
            return 'table'
        elif element.name in ['ul', 'ol']:
            return 'list'
        elif element.name == 'li':
            return 'list_item'
        else:
            return 'container'

def print_document_summary(filename: str, semantic_tree: SemanticElement) -> None:
    """Print a summary of the parsed document."""
    print(f"\n=== Document: {filename} ===")
    
    # Count elements
    counts = semantic_tree.count_elements()
    print("\nElement Counts:")
    for element_type, count in sorted(counts.items()):
        print(f"  {element_type}: {count}")
    
    # Print section titles
    print("\nSection Titles:")
    def print_sections(element: SemanticElement, level: int = 0):
        if element.element_type == 'section_title':
            print(f"{'  ' * level}{element.text}")
        for child in element.children:
            print_sections(child, level + 1)
    print_sections(semantic_tree)
    
    # Print first few paragraphs
    print("\nFirst Few Paragraphs:")
    paragraphs = []
    def collect_paragraphs(element: SemanticElement):
        if element.element_type == 'paragraph' and element.text.strip():
            paragraphs.append(element.text)
        for child in element.children:
            collect_paragraphs(child)
    collect_paragraphs(semantic_tree)
    
    for i, para in enumerate(paragraphs[:3]):
        print(f"\nParagraph {i+1}:")
        print(f"  {para[:200]}..." if len(para) > 200 else f"  {para}")

def main():
    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Example usage
    parser = SECDocumentParser()
    
    # Process all HTML files in the downloaded_html directory
    html_dir = 'downloaded_html'
    for filename in os.listdir(html_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(html_dir, filename)
            print(f"\nProcessing {filename}...")
            
            # Parse the document
            semantic_tree = parser.parse_file(file_path)
            
            # Print summary
            print_document_summary(filename, semantic_tree)
            
            # Save full structure to JSON file
            output_file = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.json")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(semantic_tree.to_dict(), f, indent=2, ensure_ascii=False)
            print(f"\nFull structure saved to: {output_file}")

if __name__ == "__main__":
    main()
