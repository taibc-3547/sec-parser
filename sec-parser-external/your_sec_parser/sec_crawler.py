import requests
from typing import List, Dict, Optional, TypedDict
from datetime import datetime
import time
import logging
from urllib.parse import urljoin
from dataclasses import dataclass
from enum import Enum

class FilingType(Enum):
    """Supported SEC filing types."""
    TEN_K = "10-K"
    TEN_Q = "10-Q"
    EIGHT_K = "8-K"
    THIRTEEN_F = "13F"

@dataclass
class FilingMetadata:
    """Metadata for a single SEC filing."""
    cik: str
    form_type: FilingType
    filing_date: datetime
    url: str
    size: int
    accession_number: str

class SECCrawler:
    """A crawler for retrieving SEC filings with proper rate limiting and error handling."""
    
    BASE_URL = "https://www.sec.gov/Archives/edgar/data"
    RATE_LIMIT_DELAY = 0.1  # 10 requests per second
    MAX_RETRIES = 3
    
    def __init__(self, user_agent: str):
        """
        Initialize the SEC crawler.
        
        Args:
            user_agent: Your user agent string (e.g., "Your Company Name (email@example.com)")
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        })
        self.logger = logging.getLogger(__name__)
    
    def _make_request(self, url: str, retries: int = MAX_RETRIES) -> Optional[requests.Response]:
        """
        Make a request with retries and rate limiting.
        
        Args:
            url: The URL to request
            retries: Number of retry attempts
            
        Returns:
            Response object if successful, None otherwise
        """
        for attempt in range(retries):
            try:
                response = self.session.get(url)
                response.raise_for_status()
                
                # Respect SEC's rate limiting
                if response.status_code == 200:
                    time.sleep(self.RATE_LIMIT_DELAY)
                return response
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {str(e)}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    self.logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
    
    def get_filing_metadata(self, cik: str, form_type: FilingType = FilingType.TEN_K, 
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> List[FilingMetadata]:
        """
        Get metadata for filings matching the criteria.
        
        Args:
            cik: Company CIK number
            form_type: Type of filing (e.g., "10-K", "10-Q")
            start_date: Start date for filings
            end_date: End date for filings
            
        Returns:
            List of filing metadata objects
        """
        url = f"{self.BASE_URL}/{cik}/index.json"
        response = self._make_request(url)
        
        if not response:
            return []
            
        try:
            data = response.json()
            filings = []
            
            for filing in data.get('directory', {}).get('item', []):
                # Check form type
                if filing.get('type') != form_type.value:
                    continue
                    
                # Check date range
                filing_date = datetime.strptime(filing.get('last-modified', ''), '%Y-%m-%d')
                if start_date and filing_date < start_date:
                    continue
                if end_date and filing_date > end_date:
                    continue
                    
                # Extract accession number from the filing name
                filing_name = filing.get('name', '')
                accession_number = filing_name.split('/')[-1].split('.')[0]
                    
                filings.append(FilingMetadata(
                    cik=cik,
                    form_type=form_type,
                    filing_date=filing_date,
                    url=urljoin(self.BASE_URL, filing_name),
                    size=filing.get('size', 0),
                    accession_number=accession_number
                ))
                
            return filings
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error parsing filing metadata: {str(e)}")
            return []
    
    def download_filing(self, filing_url: str) -> Optional[str]:
        """
        Download and return the content of a filing.
        
        Args:
            filing_url: URL of the filing to download
            
        Returns:
            Filing content as string if successful, None otherwise
        """
        response = self._make_request(filing_url)
        return response.text if response else None 