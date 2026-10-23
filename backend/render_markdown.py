import markdown
from bs4 import BeautifulSoup

def markdown_to_text(md_string: str) -> str:
    # 1. Convert Markdown to HTML
    html = markdown.markdown(md_string)
    
    # 2. Parse HTML with BeautifulSoup and extract plain text
    soup = BeautifulSoup(html, "html.parser")
    plain_text = soup.get_text()
    
    return plain_text

