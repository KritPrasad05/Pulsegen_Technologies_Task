import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import logging
import re
import warnings

warnings.filterwarnings("ignore")

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RobustCrawler:
    def __init__(self):
        self.visited = set()
        self.session = requests.Session()
        # Mimic a real browser
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def validate_url(self, url: str) -> bool:
        try:
            parsed = urlparse(url)
            return all([parsed.scheme, parsed.netloc])
        except ValueError:
            return False

    def is_internal_link(self, base_url, target_url):
        try:
            base_domain = urlparse(base_url).netloc.replace('www.', '')
            target_domain = urlparse(target_url).netloc.replace('www.', '')
            
            # Allow subdomains
            if base_domain not in target_domain and target_domain not in base_domain:
                return False
                
            # Exclude non-content pages
            exclude = ['login', 'signup', 'signin', 'logout', '#', 'javascript', 'mailto', 'tel']
            if any(x in target_url.lower() for x in exclude):
                return False
                
            return True
        except:
            return False

    def normalize_content(self, soup):
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "iframe", "form", "aside"]):
            tag.decompose()

        for table in soup.find_all("table"):
            rows = []
            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                if cells:
                    rows.append(" | ".join(cells))
            table_text = "\n" + "\n".join(rows) + "\n"
            table.replace_with(table_text)

        text = soup.get_text(separator=' ', strip=True)
        return re.sub(r'\n\s*\n', '\n\n', text)

    def fetch_page(self, url):
        try:
            time.sleep(0.5) 
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None, []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = self.normalize_content(soup)
            
            links = []
            for a in soup.find_all('a', href=True):
                full_url = urljoin(url, a['href'])
                links.append(full_url)
                
            return text, links
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None, []

    def crawl(self, start_urls, max_pages_per_domain=6):
        aggregated_content = ""
        visited_global = set()
        errors = []

        for start_url in start_urls:
            if not self.validate_url(start_url):
                errors.append(f"Invalid URL: {start_url}")
                continue

            queue = [start_url]
            domain_visited_count = 0
            
            while queue and domain_visited_count < max_pages_per_domain:
                current_url = queue.pop(0)
                
                if current_url in visited_global:
                    continue
                
                visited_global.add(current_url)
                
                text, new_links = self.fetch_page(current_url)
                
                if text:
                    domain_visited_count += 1
                    aggregated_content += f"\n\n=== PAGE START: {current_url} ===\n{text}\n=== PAGE END ===\n"
                    
                    for link in new_links:
                        if link not in visited_global and link not in queue:
                            if self.is_internal_link(start_url, link):
                                if any(k in link for k in ['doc', 'guide', 'help', 'article']):
                                    queue.insert(0, link)
                                else:
                                    queue.append(link)
                else:
                    errors.append(f"Failed: {current_url}")

        return aggregated_content, list(visited_global), errors