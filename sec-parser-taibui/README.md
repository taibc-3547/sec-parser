# SEC Document Parser

A Python-based parser for SEC (Securities and Exchange Commission) documents that converts HTML filings into structured semantic formats. Currently optimized for processing 8-K filings (Form 8-K), which are used to report significant events that shareholders should know about.

## Features

- Semantic segmentation of SEC document elements
- Hierarchical structure representation
- Special handling for tables and lists
- Confidence scoring for element classification
- Support for both human-readable and LLM-optimized output formats
- Efficient HTML parsing using BeautifulSoup4
- Optimized for 8-K filing structure and content

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd sec-parser
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your HTML files in the `downloaded_html` directory

2. Run the parser:
```bash
python enhanced_parser.py
```

3. The processed output will be available in:
   - `enhanced_output/human_output/`: Human-readable JSON files
   - `enhanced_output/llm_output/`: LLM-optimized JSON files

## Output Format

The parser generates two types of JSON outputs:

### Human-Readable Format
```json
{
  "type": "DOCUMENT",
  "content": "document content",
  "level": 0,
  "confidence": 1.0,
  "children": [
    {
      "type": "SECTION_TITLE",
      "content": "section title",
      "level": 1,
      "confidence": 0.95,
      "children": []
    }
  ]
}
```

### LLM-Optimized Format
```json
{
  "t": "DOCUMENT",
  "c": "document content",
  "l": 0,
  "ch": [
    {
      "t": "SECTION_TITLE",
      "c": "section title",
      "l": 1,
      "ch": []
    }
  ]
}
```

## Element Types

The parser recognizes the following semantic element types:
- DOCUMENT: Root element
- SECTION_TITLE: Document sections and subsections
- PARAGRAPH: Text paragraphs
- TABLE: Tabular data
- TABLE_ROW: Table rows
- TABLE_CELL: Table cells
- LIST: Ordered and unordered lists
- LIST_ITEM: List items
- TEXT: General text content
- SUPPLEMENTARY_TEXT: Notes and supplementary information
- CONTAINER: Generic container elements

## Dependencies

- beautifulsoup4>=4.12.0
- html5lib>=1.1
- typing-extensions>=4.5.0

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here] 