from agents.basic_agent import BasicAgent
import requests
from bs4 import BeautifulSoup
import urllib.parse
import logging
import time
import re

class DuckDuckGoSearchAgent(BasicAgent):
    def __init__(self):
        self.name = "DuckDuckGoSearch"
        self.metadata = {
            "name": self.name,
            "description": "Search the web using DuckDuckGo and fetch webpage content",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Action to perform: 'search' or 'fetch_content'",
                        "enum": ["search", "fetch_content"]
                    },
                    "query": {
                        "type": "string",
                        "description": "Search query (for search action)"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to fetch content from (for fetch_content action)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of search results to return (default: 10)"
                    }
                },
                "required": ["action"]
            }
        }
        self.base_url = "https://html.duckduckgo.com/html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        self.last_request_time = None
        self.min_request_interval = 2  # seconds between requests
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        action = kwargs.get('action')
        
        if action == "search":
            query = kwargs.get('query')
            max_results = kwargs.get('max_results', 10)
            
            if not query:
                return "Error: Search query is required"
            
            return self.search_duckduckgo(query, max_results)
            
        elif action == "fetch_content":
            url = kwargs.get('url')
            
            if not url:
                return "Error: URL is required for fetch_content action"
            
            return self.fetch_webpage_content(url)
            
        else:
            return f"Error: Unknown action '{action}'. Use 'search' or 'fetch_content'"

    def _apply_rate_limit(self):
        """Simple rate limiting to avoid being blocked"""
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def search_duckduckgo(self, query, max_results=10):
        """Search DuckDuckGo and return formatted results"""
        try:
            self._apply_rate_limit()
            
            # Create form data for POST request
            data = {
                "q": query,
                "b": "",
                "kl": "",
            }
            
            response = requests.post(
                self.base_url, 
                data=data, 
                headers=self.headers, 
                timeout=30
            )
            response.raise_for_status()
            
            # Parse HTML response
            soup = BeautifulSoup(response.text, 'html.parser')
            if not soup:
                return "Error: Failed to parse search results"
            
            results = []
            for result in soup.select('.result'):
                title_elem = result.select_one('.result__title')
                if not title_elem:
                    continue
                
                link_elem = title_elem.find('a')
                if not link_elem:
                    continue
                
                title = link_elem.get_text(strip=True)
                link = link_elem.get('href', '')
                
                # Skip ad results
                if 'y.js' in link:
                    continue
                
                # Clean up DuckDuckGo redirect URLs
                if link.startswith('//duckduckgo.com/l/?uddg='):
                    link = urllib.parse.unquote(link.split('uddg=')[1].split('&')[0])
                
                snippet_elem = result.select_one('.result__snippet')
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet,
                    "position": len(results) + 1
                })
                
                if len(results) >= max_results:
                    break
            
            return self._format_search_results(results)
            
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to perform search - {str(e)}"
        except Exception as e:
            logging.error(f"Search error: {str(e)}")
            return f"Error: An unexpected error occurred - {str(e)}"

    def fetch_webpage_content(self, url):
        """Fetch and extract clean text content from a webpage"""
        try:
            self._apply_rate_limit()
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Get the text content
            text = soup.get_text()
            
            # Clean up the text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Get page title
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else "No title"
            
            # Truncate if too long
            if len(text) > 8000:
                text = text[:8000] + "... [content truncated]"
            
            return f"Page Title: {title_text}\n\nContent:\n{text}"
            
        except requests.exceptions.RequestException as e:
            return f"Error: Failed to fetch content - {str(e)}"
        except Exception as e:
            logging.error(f"Fetch content error: {str(e)}")
            return f"Error: An unexpected error occurred - {str(e)}"

    def _format_search_results(self, results):
        """Format search results in a readable way"""
        if not results:
            return "No results found. This could be due to DuckDuckGo's bot detection or the query returned no matches. Please try rephrasing your search or try again in a few minutes."
        
        output = [f"Found {len(results)} search results:\n"]
        
        for result in results:
            output.append(f"{result['position']}. {result['title']}")
            output.append(f"   URL: {result['link']}")
            output.append(f"   Summary: {result['snippet']}")
            output.append("")  # Empty line between results
        
        return "\n".join(output)