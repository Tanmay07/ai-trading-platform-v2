import re
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ArticleParser:
    """Extracts clean text from HTML summaries and normalizes content."""
    
    @staticmethod
    def parse_summary(html_content: str) -> str:
        if not html_content:
            return ""
            
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            
            # Basic normalization
            text = re.sub(r'\s+', ' ', text)
            return text
        except Exception as e:
            logger.error(f"Failed to parse HTML summary: {e}")
            return html_content
