"""
Multi-Source Academic Paper Crawler
Searches and downloads metadata from arXiv, ACL Anthology, and Springer
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time
import json
from urllib.parse import quote
import os

class PaperCrawler:
    def __init__(self):
        self.arxiv_base = "http://export.arxiv.org/api/query"
        self.acl_base = "https://aclanthology.org"
        self.springer_base = "http://api.springernature.com/metadata/json"
        
    def search_arxiv(self, query: str, search_type: str = "all", max_results: int = 10) -> List[Dict]:
        """
        Search arXiv for papers
        
        Args:
            query: Search term (author name or keyword)
            search_type: 'author', 'title', 'abstract', or 'all'
            max_results: Maximum number of results to return
        """
        print(f"\n🔍 Searching arXiv for: {query}")
        
        # Format query based on search type
        if search_type == "author":
            formatted_query = f"au:{query}"
        elif search_type == "title":
            formatted_query = f"ti:{query}"
        elif search_type == "abstract":
            formatted_query = f"abs:{query}"
        else:
            formatted_query = f"all:{query}"
        
        params = {
            "search_query": formatted_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": "relevance",
            "sortOrder": "descending"
        }
        
        try:
            response = requests.get(self.arxiv_base, params=params, timeout=30)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
            papers = []
            for entry in root.findall('atom:entry', namespace):
                paper = {
                    'source': 'arXiv',
                    'title': entry.find('atom:title', namespace).text.strip().replace('\n', ' '),
                    'authors': [author.find('atom:name', namespace).text 
                                for author in entry.findall('atom:author', namespace)],
                    'abstract': entry.find('atom:summary', namespace).text.strip().replace('\n', ' '),
                    'published': entry.find('atom:published', namespace).text,
                    'url': entry.find('atom:id', namespace).text,
                    'pdf_url': next((link.attrib['href'] for link in entry.findall('atom:link', namespace) 
                                     if link.attrib.get('title') == 'pdf'), None),
                    'categories': [cat.attrib['term'] for cat in entry.findall('atom:category', namespace)]
                }
                papers.append(paper)
            
            print(f"✓ Found {len(papers)} papers on arXiv")
            return papers
            
        except Exception as e:
            print(f"✗ Error searching arXiv: {e}")
            return []
    
    def search_acl(self, query: str, search_type: str = "all", max_results: int = 10) -> List[Dict]:
        """
        Search ACL Anthology for papers
        
        Args:
            query: Search term (author name or keyword)
            search_type: 'author' or 'all'
            max_results: Maximum number of results to return
        """
        print(f"\n🔍 Searching ACL Anthology for: {query}")
        
        papers = []
        
        try:
            # ACL Anthology search endpoint
            search_url = f"https://aclanthology.org/search/"
            params = {'q': query}
            
            # Note: ACL doesn't have a public API, so we'll provide a simpler approach
            # In production, you might want to use web scraping with BeautifulSoup
            
            print("ℹ️  ACL Anthology doesn't provide a public API.")
            print(f"   Visit: https://aclanthology.org/search/?q={quote(query)}")
            print("   For programmatic access, consider using the ACL Anthology GitHub data:")
            print("   https://github.com/acl-org/acl-anthology")
            
            return papers
            
        except Exception as e:
            print(f"✗ Error searching ACL: {e}")
            return []
    
    def search_springer(self, query: str, api_key: Optional[str] = None, 
                        search_type: str = "all", max_results: int = 10) -> List[Dict]:
        """
        Search Springer for papers
        
        Args:
            query: Search term (author name or keyword)
            api_key: Springer API key (required - get from https://dev.springernature.com/)
            search_type: 'name' (author) or 'keyword'
            max_results: Maximum number of results to return
        """
        print(f"\n🔍 Searching Springer for: {query}")
        
        if not api_key:
            print("✗ Springer API key required. Get one at: https://dev.springernature.com/")
            return []
        
        try:
            params = {
                "q": f'name:"{query}"' if search_type == "name" else f'keyword:"{query}"',
                "api_key": api_key,
                "p": max_results,
                "s": 1
            }
            
            response = requests.get(self.springer_base, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            papers = []
            
            for record in data.get('records', []):
                paper = {
                    'source': 'Springer',
                    'title': record.get('title', 'N/A'),
                    'authors': [creator.get('creator', '') for creator in record.get('creators', [])],
                    'abstract': record.get('abstract', 'N/A'),
                    'published': record.get('publicationDate', 'N/A'),
                    'url': record.get('url', [{}])[0].get('value', 'N/A'),
                    'doi': record.get('doi', 'N/A'),
                    'publisher': record.get('publisher', 'N/A'),
                    'journal': record.get('publicationName', 'N/A')
                }
                papers.append(paper)
            
            print(f"✓ Found {len(papers)} papers on Springer")
            return papers
            
        except Exception as e:
            print(f"✗ Error searching Springer: {e}")
            return []
    
    def search_all(self, query: str, search_type: str = "all", 
                   max_results: int = 10, springer_api_key: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Search all sources for papers
        
        Args:
            query: Search term
            search_type: Type of search ('author', 'keyword', or 'all')
            max_results: Maximum results per source
            springer_api_key: API key for Springer
        """
        results = {
            'arXiv': [],
            'ACL': [],
            'Springer': []
        }
        
        # --- Search arXiv ---
        # arXiv supports: 'author', 'title', 'abstract', 'all'
        results['arXiv'] = self.search_arxiv(query, search_type, max_results)
        time.sleep(1)  # Rate limiting
        
        # --- Search ACL ---
        # ACL search is manual, so type doesn't matter much
        results['ACL'] = self.search_acl(query, search_type, max_results)
        time.sleep(1)
        
        # --- Search Springer ---
        if springer_api_key:
            # Map search_type to Springer's types
            springer_type = "name" if search_type == "author" else "keyword"
            results['Springer'] = self.search_springer(query, springer_api_key, springer_type, max_results)
        else:
            print("\nℹ️  Skipping Springer (no API key provided)")
        
        return results
    
    def save_results(self, results: Dict[str, List[Dict]], filename: str = "papers.json"):
        """Save search results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Results saved to {filename}")
    
    def display_results(self, results: Dict[str, List[Dict]]):
        """Display search results in a readable format"""
        total = sum(len(papers) for papers in results.values())
        print(f"\n{'='*80}")
        print(f"SEARCH RESULTS SUMMARY - Total: {total} papers found")
        print(f"{'='*80}")
        
        for source, papers in results.items():
            if papers:
                print(f"\n{source} ({len(papers)} papers):")
                print("-" * 80)
                for i, paper in enumerate(papers, 1):
                    print(f"\n{i}. {paper['title']}")
                    print(f"   Authors: {', '.join(paper['authors'][:3])}" + 
                          (" et al." if len(paper['authors']) > 3 else ""))
                    print(f"   Published: {paper['published']}")
                    print(f"   URL: {paper['url']}")

# --- New Helper Functions for User Input ---

def get_api_key() -> Optional[str]:
    """
    Get Springer API key from environment variable or user input.
    Recommended: Set SPRINGER_API_KEY as an environment variable.
    """
    api_key = os.getenv("SPRINGER_API_KEY")
    if api_key:
        print("✓ Found Springer API key in environment variable (SPRINGER_API_KEY).")
        return api_key
    
    print("\n--- Springer API Key ---")
    print("To search Springer, an API key is required.")
    print("You can get one from: https://dev.springernature.com/")
    print("Alternatively, you can set it as an environment variable named 'SPRINGER_API_KEY'.")
    
    api_key = input("Enter your Springer API key (or press Enter to skip Springer): ").strip()
    return api_key if api_key else None

def get_search_type() -> str:
    """Helper function to get validated search type from user."""
    print("\nSelect search type:")
    print("  1: All (General keyword search)")
    print("  2: Author")
    print("  3: Title (arXiv specific)")
    print("  4: Abstract (arXiv specific)")
    
    type_map = {
        '1': 'all',
        '2': 'author',
        '3': 'title',
        '4': 'abstract'
    }
    
    while True:
        choice = input("Enter choice (1-4): ").strip()
        if choice in type_map:
            return type_map[choice]
        else:
            print("Invalid choice. Please enter a number between 1 and 4.")

def get_max_results() -> int:
    """Helper function to get validated max results from user."""
    while True:
        try:
            results_str = input("Enter max results per source (default: 10): ").strip()
            if not results_str:
                return 10
            max_res = int(results_str)
            if max_res > 0:
                return max_res
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

# --- New Interactive Main Function ---

def main():
    """Main interactive loop for the Paper Crawler."""
    crawler = PaperCrawler()
    print("="*80)
    print("📚 Welcome to the Multi-Source Academic Paper Crawler 📚")
    print("="*80)
    
    # Get API key once at the start
    springer_api_key = get_api_key()
    
    while True:
        print("\n" + "-"*80)
        print("🚀 Starting a new search...")
        
        # 1. Get Search Query
        query = input("Enter your search query (e.g., 'NLP', 'Geoffrey Hinton'): ").strip()
        if not query:
            print("Search query cannot be empty. Please try again.")
            continue
            
        # 2. Get Search Type
        search_type = get_search_type()
        
        # 3. Get Max Results
        max_results = get_max_results()
        
        # 4. Get Filename
        # Create a safe default filename
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '_')).rstrip()
        default_filename = f"{safe_query.replace(' ', '_')}_{search_type}.json"
        
        filename = input(f"Enter filename to save results (default: {default_filename}): ").strip()
        if not filename:
            filename = default_filename
        
        # 5. Run the search
        results = crawler.search_all(
            query=query,
            search_type=search_type,
            max_results=max_results,
            springer_api_key=springer_api_key
        )
        
        # 6. Display and Save Results
        if any(results.values()):
            crawler.display_results(results)
            crawler.save_results(results, filename)
        else:
            print("\n" + "="*80)
            print("SEARCH RESULTS SUMMARY - No papers found.")
            print("="*80)

        # 7. Continue?
        print("-" * 80)
        another = input("Do you want to perform another search? (y/n): ").strip().lower()
        if another != 'y':
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    # Make sure you have the 'requests' package installed:
    # pip install requests
    main()
