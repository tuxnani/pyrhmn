import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import os
import time
from collections import deque
import json

class TeluguWebScraper:
    def __init__(self, base_url="https://www.eenadu.net/", max_depth=3, delay=1):
        """
        Initialize the scraper
        
        Args:
            base_url: Starting URL (default: eenadu.net)
            max_depth: Maximum depth to crawl (default: 3)
            delay: Delay between requests in seconds (default: 1)
        """
        self.base_url = base_url
        self.max_depth = max_depth
        self.delay = delay
        self.visited_urls = set()
        self.domain = urlparse(base_url).netloc
        
        # Create output directories
        os.makedirs("html_files", exist_ok=True)
        os.makedirs("text_files", exist_ok=True)
        os.makedirs("parsed_content", exist_ok=True)
        
        # Telugu Unicode range: \u0C00-\u0C7F
        self.telugu_pattern = re.compile(r'[\u0C00-\u0C7F]+')
        # English words pattern
        self.english_pattern = re.compile(r'\b[A-Za-z]{2,}\b')
        
        # Headers to mimic browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain"""
        parsed = urlparse(url)
        return (parsed.netloc == self.domain and 
                parsed.scheme in ['http', 'https'] and
                not url.endswith(('.pdf', '.jpg', '.png', '.gif', '.mp4', '.zip')))
    
    def fetch_html(self, url):
        """Fetch HTML content from URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def save_html(self, url, html_content, level):
        """Save HTML content to file"""
        # Create safe filename from URL
        filename = re.sub(r'[^\w\-]', '_', url.replace('https://', '').replace('http://', ''))
        filename = f"level{level}_{filename[:150]}.html"
        filepath = os.path.join("html_files", filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return filepath
        except Exception as e:
            print(f"Error saving HTML {filepath}: {str(e)}")
            return None
    
    def html_to_text(self, html_content):
        """Extract text from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def save_text(self, text, html_filepath):
        """Save extracted text to file"""
        text_filename = os.path.basename(html_filepath).replace('.html', '.txt')
        text_filepath = os.path.join("text_files", text_filename)
        
        try:
            with open(text_filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            return text_filepath
        except Exception as e:
            print(f"Error saving text {text_filepath}: {str(e)}")
            return None
    
    def extract_telugu_english(self, text):
        """Extract Telugu and English content from text"""
        lines = text.split('\n')
        filtered_content = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Check if line contains Telugu
            has_telugu = bool(self.telugu_pattern.search(line))
            
            # Check if line contains English words
            english_words = self.english_pattern.findall(line)
            has_english = len(english_words) >= 2  # At least 2 English words
            
            # Include if has Telugu or meaningful English
            if has_telugu or has_english:
                # Filter out navigation/menu items (usually very short)
                if len(line) > 15 or has_telugu:
                    filtered_content.append(line)
        
        return filtered_content
    
    def save_parsed_content(self, content_lines, text_filepath):
        """Save parsed Telugu/English content"""
        parsed_filename = os.path.basename(text_filepath).replace('.txt', '_parsed.txt')
        parsed_filepath = os.path.join("parsed_content", parsed_filename)
        
        try:
            with open(parsed_filepath, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content_lines))
            return parsed_filepath
        except Exception as e:
            print(f"Error saving parsed content {parsed_filepath}: {str(e)}")
            return None
    
    def extract_links(self, html_content, current_url):
        """Extract all links from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set()
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(current_url, href)
            
            if self.is_valid_url(full_url):
                links.add(full_url)
        
        return links
    
    def crawl(self):
        """Main crawling method using BFS"""
        # Queue: (url, depth)
        queue = deque([(self.base_url, 0)])
        self.visited_urls.add(self.base_url)
        
        stats = {
            'pages_crawled': 0,
            'pages_by_level': {i: 0 for i in range(self.max_depth + 1)},
            'errors': 0
        }
        
        print(f"Starting crawl from: {self.base_url}")
        print(f"Maximum depth: {self.max_depth}")
        print("-" * 80)
        
        while queue:
            current_url, depth = queue.popleft()
            
            if depth > self.max_depth:
                continue
            
            print(f"\nLevel {depth}: Crawling {current_url}")
            
            # Fetch HTML
            html_content = self.fetch_html(current_url)
            if not html_content:
                stats['errors'] += 1
                continue
            
            # Save HTML
            html_filepath = self.save_html(current_url, html_content, depth)
            if not html_filepath:
                continue
            
            # Extract text
            text_content = self.html_to_text(html_content)
            text_filepath = self.save_text(text_content, html_filepath)
            
            # Parse for Telugu/English
            if text_filepath:
                parsed_lines = self.extract_telugu_english(text_content)
                parsed_filepath = self.save_parsed_content(parsed_lines, text_filepath)
                
                if parsed_filepath:
                    print(f"  ✓ Saved {len(parsed_lines)} filtered lines")
            
            stats['pages_crawled'] += 1
            stats['pages_by_level'][depth] += 1
            
            # Extract and queue links for next level
            if depth < self.max_depth:
                links = self.extract_links(html_content, current_url)
                new_links = links - self.visited_urls
                
                print(f"  Found {len(new_links)} new links at level {depth}")
                
                for link in new_links:
                    if link not in self.visited_urls:
                        queue.append((link, depth + 1))
                        self.visited_urls.add(link)
            
            # Rate limiting
            time.sleep(self.delay)
        
        # Print summary
        print("\n" + "=" * 80)
        print("CRAWLING COMPLETED")
        print("=" * 80)
        print(f"Total pages crawled: {stats['pages_crawled']}")
        print(f"Total errors: {stats['errors']}")
        print("\nPages by level:")
        for level, count in stats['pages_by_level'].items():
            print(f"  Level {level}: {count} pages")
        
        # Save stats
        with open('crawl_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        return stats


def main():
    """Main function"""
    print("=" * 80)
    print("TELUGU WEB SCRAPER")
    print("=" * 80)
    
    # Get user input
    url = input("\nEnter URL to scrape (press Enter for default: https://www.eenadu.net/): ").strip()
    if not url:
        url = "https://www.eenadu.net/"
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        max_depth = int(input("Enter maximum depth (1-5, press Enter for 3): ").strip() or "3")
        max_depth = max(1, min(5, max_depth))  # Clamp between 1 and 5
    except ValueError:
        max_depth = 3
    
    try:
        delay = float(input("Enter delay between requests in seconds (press Enter for 1): ").strip() or "1")
        delay = max(0.5, delay)  # Minimum 0.5 seconds
    except ValueError:
        delay = 1
    
    # Create scraper and start crawling
    scraper = TeluguWebScraper(base_url=url, max_depth=max_depth, delay=delay)
    scraper.crawl()
    
    print("\nOutput directories:")
    print("  - html_files/      : Original HTML files")
    print("  - text_files/      : Extracted text from HTML")
    print("  - parsed_content/  : Filtered Telugu and English content")
    print("  - crawl_stats.json : Crawling statistics")


if __name__ == "__main__":
    main()