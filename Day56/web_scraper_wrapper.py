import requests
import time
import logging
from typing import Optional, Dict

# Set up basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class ScrapingWrapper:
    """
    A robust web scraping wrapper designed for ethical scraping with 
    rate limiting and comprehensive error handling.
    """
    
    def __init__(self, delay_seconds: float = 2.0, max_retries: int = 3, **kwargs):
        """
        Initializes the scraper with rate limiting and retry settings.
        
        Args:
            delay_seconds: Minimum time to wait between consecutive requests.
            max_retries: Maximum number of times to retry a failed request.
            **kwargs: Additional arguments for requests.Session (e.g., headers).
        """
        self.delay_seconds = delay_seconds
        self.max_retries = max_retries
        self.last_request_time = 0.0
        
        # Use a session for connection pooling and header persistence
        self.session = requests.Session()
        
        # Set default headers to mimic a common browser
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
        }
        self.session.headers.update(default_headers)
        self.session.headers.update(kwargs.get('headers', {}))
        
        logging.info(f"Scraper initialized with rate limit: {delay_seconds}s and {max_retries} retries.")

    def _rate_limit_delay(self):
        """
        Enforces a minimum delay between requests.
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay_seconds:
            wait_time = self.delay_seconds - elapsed
            logging.info(f"Rate limiting: Waiting for {wait_time:.2f} seconds.")
            time.sleep(wait_time)
        self.last_request_time = time.time()

    def fetch_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetches the content of a URL with rate limiting and error handling.
        
        Args:
            url: The URL to fetch.
            timeout: The maximum number of seconds to wait for a response.
            
        Returns:
            The text content of the response if successful, otherwise None.
        """
        for attempt in range(self.max_retries):
            self._rate_limit_delay()
            
            try:
                logging.info(f"Fetching URL: {url} (Attempt {attempt + 1}/{self.max_retries})")
                
                response = self.session.get(url, timeout=timeout)
                
                # Check for successful HTTP status codes (200-299)
                response.raise_for_status()
                
                logging.info(f"Successfully fetched {url}. Status: {response.status_code}")
                return response.text
                
            except requests.exceptions.ConnectionError as e:
                logging.error(f"Connection Error for {url}: {e}")
            except requests.exceptions.Timeout:
                logging.error(f"Timeout occurred while fetching {url}.")
            except requests.exceptions.HTTPError as e:
                # Handle 4xx (Client) and 5xx (Server) errors
                logging.error(f"HTTP Error for {url} ({response.status_code}): {e}")
                
                # Do not retry on 404/403 errors, as they are unlikely to resolve
                if response.status_code in [404, 403]:
                    logging.warning("Non-retryable HTTP status code detected (404/403). Aborting retries.")
                    break
            except requests.exceptions.RequestException as e:
                # Catch all other requests errors
                logging.error(f"An unexpected error occurred during request for {url}: {e}")
            
            # If this was not the last attempt, wait before retrying
            if attempt < self.max_retries - 1:
                # Exponential backoff for retries
                retry_wait = self.delay_seconds * (2 ** attempt)
                logging.info(f"Retrying in {retry_wait:.2f} seconds...")
                time.sleep(retry_wait)
        
        logging.error(f"Failed to fetch {url} after {self.max_retries} attempts.")
        return None

# --- Example Usage ---
if __name__ == "__main__":
    
    # NOTE: The URLs below are for demonstration. Use real URLs when running.
    # To demonstrate errors, you might need a URL that often fails or times out.
    
    test_urls = [
        "https://www.google.com/search?q=test_query", # Expected: Success
        "https://httpbin.org/delay/5",                 # Expected: Timeout (since timeout=3)
        "https://httpbin.org/status/404",               # Expected: 404 Error (Non-retryable)
        "https://www.example.com",                     # Expected: Success
    ]
    
    # 1. Initialize the wrapper with a 1-second delay and a 3-second timeout
    scraper = ScrapingWrapper(delay_seconds=1.0, max_retries=2)
    
    results = {}
    
    for url in test_urls:
        # Use a short timeout (3 seconds) to test the timeout handling
        content = scraper.fetch_url(url, timeout=3) 
        
        if content:
            # Simple check of content length
            results[url] = f"Content length: {len(content)} bytes"
        else:
            results[url] = "Failed to retrieve content."

    print("\n--- Summary of Fetch Results ---")
    for url, status in results.items():
        print(f"URL: {url}\nStatus: {status}\n")
