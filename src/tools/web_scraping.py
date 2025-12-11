"""
Web scraping tools for Project OMNI - Phase 2.
Provides BeautifulSoup and requests integration.
"""

import logging
from typing import Dict, Any, List, Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class WebScrapingTools:
    """Tools for web scraping and data extraction."""
    
    def __init__(self):
        """Initialize web scraping tools."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_page(self, url: str, timeout: int = 30) -> str:
        """
        Fetch a web page.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content
        """
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            logger.info(f"Fetched page: {url}")
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            raise
    
    def extract_links(self, html: str, base_url: Optional[str] = None) -> List[str]:
        """
        Extract all links from HTML.
        
        Args:
            html: HTML content
            base_url: Base URL for relative links
            
        Returns:
            List of URLs
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if base_url and not href.startswith('http'):
                    from urllib.parse import urljoin
                    href = urljoin(base_url, href)
                links.append(href)
            
            logger.info(f"Extracted {len(links)} links")
            return links
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            raise
    
    def extract_text(self, html: str, selector: Optional[str] = None) -> str:
        """
        Extract text from HTML.
        
        Args:
            html: HTML content
            selector: CSS selector (optional)
            
        Returns:
            Extracted text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            if selector:
                elements = soup.select(selector)
                text = ' '.join([el.get_text(strip=True) for el in elements])
            else:
                text = soup.get_text(strip=True, separator=' ')
            
            logger.info(f"Extracted {len(text)} characters of text")
            return text
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            raise
    
    def scrape_table(self, html: str, table_index: int = 0) -> List[Dict[str, str]]:
        """
        Scrape a table from HTML.
        
        Args:
            html: HTML content
            table_index: Index of table to scrape (0-based)
            
        Returns:
            List of dictionaries representing table rows
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.find_all('table')
            
            if table_index >= len(tables):
                raise ValueError(f"Table index {table_index} out of range")
            
            table = tables[table_index]
            headers = [th.get_text(strip=True) for th in table.find_all('th')]
            
            rows = []
            for tr in table.find_all('tr')[1:]:  # Skip header row
                cells = [td.get_text(strip=True) for td in tr.find_all('td')]
                if cells:
                    row_dict = dict(zip(headers, cells))
                    rows.append(row_dict)
            
            logger.info(f"Scraped table with {len(rows)} rows")
            return rows
        except Exception as e:
            logger.error(f"Error scraping table: {e}")
            raise
