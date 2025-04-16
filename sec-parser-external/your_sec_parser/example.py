from your_sec_parser import SECParser

def main():
    # Initialize parser
    parser = SECParser()
    
    # Example HTML (you can replace this with actual SEC filing HTML)
    html = """
    <h1>Section 1</h1>
    <p>Some text content</p>
    <table>
        <tr><th>Header 1</th><th>Header 2</th></tr>
        <tr><td>Data 1</td><td>Data 2</td></tr>
    </table>
    <h2>Subsection 1.1</h2>
    <p>More text content</p>
    """
    
    # Parse the document
    elements = parser.parse(html)
    
    # Process the elements
    for element in elements:
        print(f"Type: {element.__class__.__name__}")
        print(f"Section: {element.section}")
        print(f"Text: {element.text[:100]}...")
        print("-" * 80)
        
        if isinstance(element, TableElement):
            table_data = element.get_table_data()
            print(f"Table data: {table_data}")

if __name__ == "__main__":
    main() 