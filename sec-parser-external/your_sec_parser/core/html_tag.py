from bs4 import Tag

class HtmlTag:
    def __init__(self, tag: Tag):
        self.tag = tag
    
    @property
    def text(self) -> str:
        return self.tag.get_text(strip=True)
    
    @property
    def name(self) -> str:
        return self.tag.name
    
    def get_source_code(self) -> str:
        return str(self.tag) 