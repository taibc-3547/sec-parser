from ..core.abstract_semantic_element import AbstractSemanticElement

class TableElement(AbstractSemanticElement):
    def get_table_data(self) -> list[list[str]]:
        rows = []
        for row in self._html_tag.tag.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            rows.append(cells)
        return rows 