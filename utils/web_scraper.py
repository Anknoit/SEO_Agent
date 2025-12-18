import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from config import USER_AGENT, REQUEST_TIMEOUT, MAX_CONTENT_LENGTH

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT
        })
    
    def fetch_url(self, url):
        """Fetch and parse a URL"""
        try:
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return None, "URL does not return HTML content"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract key information
            data = {
                'url': url,
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'meta_keywords': self._get_meta_keywords(soup),
                'headers': self._get_headers(soup),
                'content': self._get_main_content(soup)[:MAX_CONTENT_LENGTH],
                'links': self._get_links(soup, url),
                'images': self._get_images(soup),
                'status_code': response.status_code,
                'response_time': response.elapsed.total_seconds()
            }
            
            return data, None
            
        except requests.exceptions.RequestException as e:
            return None, f"Error fetching URL: {str(e)}"
    
    def _get_title(self, soup):
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else "No title found"
    
    def _get_meta_description(self, soup):
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc['content'].strip() if meta_desc else "No meta description"
    
    def _get_meta_keywords(self, soup):
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        return meta_keywords['content'].strip() if meta_keywords else "No meta keywords"
    
    def _get_headers(self, soup):
        headers = {}
        for i in range(1, 7):
            h_tags = soup.find_all(f'h{i}')
            headers[f'h{i}'] = [h.text.strip() for h in h_tags]
        return headers
    
    def _get_main_content(self, soup):
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text from main, article, or body
        main_content = soup.find('main') or soup.find('article') or soup.find('body')
        return main_content.get_text(separator=' ', strip=True) if main_content else ""
    
    def _get_links(self, soup, base_url):
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            link_text = link.text.strip()[:100]
            links.append({
                'text': link_text,
                'url': full_url,
                'is_internal': self._is_internal_url(full_url, base_url)
            })
        return links
    
    def _get_images(self, soup):
        images = []
        for img in soup.find_all('img', src=True):
            alt_text = img.get('alt', '')
            images.append({
                'src': img['src'],
                'alt': alt_text,
                'has_alt': bool(alt_text.strip())
            })
        return images
    
    def _is_internal_url(self, url, base_url):
        base_domain = urlparse(base_url).netloc
        url_domain = urlparse(url).netloc
        return base_domain == url_domain or not url_domain