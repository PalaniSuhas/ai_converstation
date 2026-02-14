"""
Brave Search API integration for real-time data
"""

import os
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class BraveSearch:
    """
    Brave Search API client for fetching real-time information
    """
    
    def __init__(self):
        """Initialize Brave Search client"""
        self.api_key = os.getenv("BRAVE_API_KEY")
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            print("[BRAVE SEARCH] API key not found. Real-time search disabled.")
    
    def search(self, query: str, count: int = 3) -> Optional[str]:
        """
        Search using Brave API
        
        Args:
            query: Search query
            count: Number of results to return
            
        Returns:
            Formatted search results or None if disabled/error
        """
        if not self.enabled:
            return None
        
        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": count,
                "text_decorations": False,
                "search_lang": "en"
            }
            
            response = requests.get(
                self.base_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return self._format_results(data)
            else:
                print(f"[BRAVE SEARCH] Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[BRAVE SEARCH] Exception: {e}")
            return None
    
    def _format_results(self, data: Dict) -> str:
        """
        Format search results into readable text
        
        Args:
            data: Raw API response
            
        Returns:
            Formatted results string
        """
        results = []
        web_results = data.get("web", {}).get("results", [])
        
        for idx, result in enumerate(web_results[:3], 1):
            title = result.get("title", "")
            description = result.get("description", "")
            url = result.get("url", "")
            
            results.append(f"{idx}. {title}")
            if description:
                results.append(f"   {description}")
            results.append(f"   Source: {url}")
            results.append("")
        
        if results:
            return "\n".join(results)
        else:
            return "No results found."
    
    def get_company_updates(self, company_name: str) -> Optional[str]:
        """
        Get latest company news and updates
        
        Args:
            company_name: Company name
            
        Returns:
            Latest updates or None
        """
        query = f"{company_name} latest news earnings stock price"
        return self.search(query, count=3)
    
    def get_market_data(self, topic: str) -> Optional[str]:
        """
        Get market data and trends
        
        Args:
            topic: Market topic (e.g., "EV market", "AI industry")
            
        Returns:
            Market insights or None
        """
        query = f"{topic} market trends 2024 2025"
        return self.search(query, count=3)
    
    def get_competitor_info(self, company: str, industry: str) -> Optional[str]:
        """
        Get competitor information
        
        Args:
            company: Company name
            industry: Industry sector
            
        Returns:
            Competitor insights or None
        """
        query = f"{company} competitors {industry} market share"
        return self.search(query, count=3)

# Singleton instance
_brave_instance = None

def get_brave_search() -> BraveSearch:
    """Get or create Brave Search singleton"""
    global _brave_instance
    if _brave_instance is None:
        _brave_instance = BraveSearch()
    return _brave_instance