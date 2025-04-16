from typing import List, Dict
import json
import csv
from datetime import datetime
import os
from .core.parser import SECParser
from .elements.abstract_semantic_element import AbstractSemanticElement

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        """
        Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        self.parser = SECParser()
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_report(self, filing_content: str, filing_metadata: Dict) -> Dict:
        """
        Generate a report for a single filing.
        
        Args:
            filing_content: Content of the SEC filing
            filing_metadata: Metadata about the filing
            
        Returns:
            Dictionary containing the report data
        """
        # Parse the filing
        elements = self.parser.parse(filing_content)
        
        # Extract key information
        report = {
            'metadata': filing_metadata,
            'sections': self._extract_sections(elements),
            'tables': self._extract_tables(elements),
            'statistics': self._generate_statistics(elements)
        }
        
        return report
    
    def save_report(self, report: Dict, format: str = 'json') -> str:
        """
        Save the report to a file.
        
        Args:
            report: Report data to save
            format: Output format ('json' or 'csv')
            
        Returns:
            Path to the saved report
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{timestamp}.{format}"
        filepath = os.path.join(self.output_dir, filename)
        
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
        elif format == 'csv':
            self._save_csv_report(report, filepath)
        
        return filepath
    
    def _extract_sections(self, elements: List[AbstractSemanticElement]) -> Dict:
        """Extract section information from parsed elements."""
        sections = {}
        current_section = None
        
        for element in elements:
            if element.section != current_section:
                current_section = element.section
                if current_section:
                    sections[current_section] = {
                        'text': element.text,
                        'element_count': 0
                    }
            
            if current_section:
                sections[current_section]['element_count'] += 1
        
        return sections
    
    def _extract_tables(self, elements: List[AbstractSemanticElement]) -> List[Dict]:
        """Extract table information from parsed elements."""
        tables = []
        for element in elements:
            if hasattr(element, 'get_table_data'):
                table_data = element.get_table_data()
                tables.append({
                    'section': element.section,
                    'rows': len(table_data),
                    'columns': len(table_data[0]) if table_data else 0,
                    'data': table_data
                })
        return tables
    
    def _generate_statistics(self, elements: List[AbstractSemanticElement]) -> Dict:
        """Generate statistics about the parsed filing."""
        stats = {
            'total_elements': len(elements),
            'section_count': len(set(e.section for e in elements if e.section)),
            'table_count': sum(1 for e in elements if hasattr(e, 'get_table_data')),
            'text_length': sum(len(e.text) for e in elements)
        }
        return stats
    
    def _save_csv_report(self, report: Dict, filepath: str) -> None:
        """Save report data in CSV format."""
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write metadata
            writer.writerow(['Metadata'])
            for key, value in report['metadata'].items():
                writer.writerow([key, value])
            
            # Write sections
            writer.writerow([])
            writer.writerow(['Sections'])
            writer.writerow(['Section Name', 'Element Count'])
            for section, data in report['sections'].items():
                writer.writerow([section, data['element_count']])
            
            # Write tables
            writer.writerow([])
            writer.writerow(['Tables'])
            writer.writerow(['Section', 'Rows', 'Columns'])
            for table in report['tables']:
                writer.writerow([table['section'], table['rows'], table['columns']])
            
            # Write statistics
            writer.writerow([])
            writer.writerow(['Statistics'])
            for key, value in report['statistics'].items():
                writer.writerow([key, value]) 