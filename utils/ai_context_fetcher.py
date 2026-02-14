"""
AI-Driven Context Fetcher - NO HARDCODING
Uses web search and AI reasoning to gather all information dynamically
"""

import os
import time
import asyncio
from typing import Optional, Dict, List
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types

load_dotenv()

class AIContextFetcher:
    """
    Fully AI-driven context fetcher
    No hardcoded company data - everything from web search + AI analysis
    """
    
    def __init__(self):
        # Initialize Gemini for AI reasoning
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            self.client = genai.Client(api_key=api_key)
            self.model_name = "gemini-2.5-flash"
        else:
            self.client = None
            print("[WARNING] No Gemini API key - AI reasoning disabled")
        
        # Initialize Brave for web search
        self.brave_key = os.getenv("BRAVE_API_KEY")
        self.brave_enabled = bool(self.brave_key)
        self.base_url = "https://api.search.brave.com/res/v1/web/search"
        
        if not self.brave_enabled:
            print("[WARNING] No Brave API key - web search disabled")
        
        # Rate limiting
        self.last_search = 0
        self.search_delay = 2  # seconds between searches
    
    async def get_company_context_ai(self, company_name: str) -> str:
        """
        Get company context through AI-driven research
        
        Args:
            company_name: Company name
            
        Returns:
            AI-generated context based on web research
        """
        print(f"\n[AI RESEARCH] Gathering intelligence on {company_name}...")
        print("[AI] No hardcoded data - researching from scratch\n")
        
        # Step 1: AI decides what to research
        research_plan = await self._ai_create_research_plan(company_name, "company")
        
        # Step 2: Execute searches based on AI plan
        search_results = await self._execute_research_plan(research_plan)
        
        # Step 3: AI synthesizes context from search results
        context = await self._ai_synthesize_context(company_name, search_results, "company")
        
        return context
    
    async def get_investor_context_ai(self, investor_name: str) -> str:
        """
        Get investor context through AI-driven research
        
        Args:
            investor_name: Investor name
            
        Returns:
            AI-generated context based on web research
        """
        print(f"\n[AI RESEARCH] Gathering intelligence on {investor_name}...")
        print("[AI] No hardcoded data - researching from scratch\n")
        
        # Step 1: AI decides what to research
        research_plan = await self._ai_create_research_plan(investor_name, "investor")
        
        # Step 2: Execute searches based on AI plan
        search_results = await self._execute_research_plan(research_plan)
        
        # Step 3: AI synthesizes context from search results
        context = await self._ai_synthesize_context(investor_name, search_results, "investor")
        
        return context
    
    async def _ai_create_research_plan(self, entity_name: str, entity_type: str) -> List[str]:
        """
        AI creates research plan - decides what to search for
        
        Args:
            entity_name: Name of company or investor
            entity_type: "company" or "investor"
            
        Returns:
            List of search queries AI wants to execute
        """
        if not self.client:
            return [f"{entity_name} latest news"]  # Fallback
        
        prompt = f"""You are a financial analyst preparing for a negotiation. You need to research {entity_name} ({entity_type}).

Your task: Create a research plan by deciding what information you need to find via web search.

For a {entity_type}, what specific searches should we run? Generate 5-8 search queries that will help you understand:

For COMPANY:
- Current valuation / market cap / stock price
- Recent financial performance (revenue, growth, margins)
- Key products and competitive advantages
- Recent news and developments
- Market position and competition
- Growth drivers and future plans
- Key risks and challenges
- Comparable company valuations

For INVESTOR:
- AUM (assets under management)
- Investment focus and strategy
- Recent investments and portfolio
- Investment criteria and preferences
- Typical check sizes and deal terms
- Value-add capabilities
- Negotiation style and approach

Generate ONLY the search queries, one per line. Be specific and current (use 2026 in queries).

Example format:
Tesla current market cap stock price February 2026
Tesla Q4 2024 earnings revenue growth
Tesla competitive advantages vs BYD NIO
Tesla latest news developments 2026
EV market trends competition 2026

NOW generate your research queries for {entity_name}:"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)]
                )],
                config=types.GenerateContentConfig(
                    temperature=0.3,  # Lower for focused queries
                    max_output_tokens=500,
                )
            )
            
            # Parse queries from response
            queries = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and len(line) > 10:
                    # Clean up query
                    line = line.lstrip('- •*1234567890.')
                    if line:
                        queries.append(line.strip())
            
            print(f"[AI RESEARCH PLAN] Generated {len(queries)} search queries:")
            for i, q in enumerate(queries[:8], 1):  # Limit to 8
                print(f"  {i}. {q}")
            print()
            
            return queries[:8]  # Limit to 8 searches
            
        except Exception as e:
            print(f"[ERROR] AI research planning failed: {e}")
            # Fallback to basic queries
            if entity_type == "company":
                return [
                    f"{entity_name} current market cap stock price 2026",
                    f"{entity_name} latest earnings revenue growth 2026",
                    f"{entity_name} competitive advantages market position",
                    f"{entity_name} latest news developments 2026"
                ]
            else:
                return [
                    f"{entity_name} AUM assets under management 2026",
                    f"{entity_name} investment focus strategy portfolio",
                    f"{entity_name} recent investments deals 2026"
                ]
    
    async def _execute_research_plan(self, queries: List[str]) -> Dict[str, str]:
        """
        Execute web searches for each query
        
        Args:
            queries: List of search queries
            
        Returns:
            Dict mapping query to search results
        """
        results = {}
        
        for i, query in enumerate(queries):
            # Rate limiting
            current_time = time.time()
            time_since_last = current_time - self.last_search
            if time_since_last < self.search_delay:
                wait_time = self.search_delay - time_since_last
                print(f"[RATE LIMIT] Waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
            
            # Execute search
            search_result = await self._web_search(query)
            if search_result:
                results[query] = search_result
                print(f"[SEARCH {i+1}/{len(queries)}] ✓ {query[:60]}...")
            else:
                print(f"[SEARCH {i+1}/{len(queries)}] ✗ {query[:60]}... (failed)")
            
            self.last_search = time.time()
        
        print(f"\n[RESEARCH COMPLETE] Gathered {len(results)} sources\n")
        return results
    
    async def _web_search(self, query: str, count: int = 5) -> Optional[str]:
        """
        Execute Brave web search
        
        Args:
            query: Search query
            count: Number of results
            
        Returns:
            Formatted search results or None
        """
        if not self.brave_enabled:
            return None
        
        try:
            import requests
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.brave_key
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
                return self._format_search_results(data)
            elif response.status_code == 429:
                print(f"[RATE LIMIT] Brave API rate limited")
                return None
            else:
                print(f"[ERROR] Brave search failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Search exception: {e}")
            return None
    
    def _format_search_results(self, data: Dict) -> str:
        """Format search results into readable text"""
        results = []
        web_results = data.get("web", {}).get("results", [])
        
        for idx, result in enumerate(web_results[:5], 1):
            title = result.get("title", "")
            description = result.get("description", "")
            url = result.get("url", "")
            
            if title or description:
                results.append(f"[{idx}] {title}")
                if description:
                    results.append(f"    {description}")
                results.append(f"    Source: {url}")
                results.append("")
        
        return "\n".join(results) if results else "No results"
    
    async def _ai_synthesize_context(self, entity_name: str, search_results: Dict[str, str], entity_type: str) -> str:
        """
        AI synthesizes all search results into structured context
        
        Args:
            entity_name: Name of entity
            search_results: Dict of search results
            entity_type: "company" or "investor"
            
        Returns:
            AI-synthesized context
        """
        if not self.client:
            # Fallback - return raw results
            context = f"{entity_type.upper()}: {entity_name}\n\n"
            for query, results in search_results.items():
                context += f"\n{query}:\n{results}\n"
            return context
        
        # Combine all search results
        all_results = ""
        for query, results in search_results.items():
            all_results += f"\n### Search: {query}\n{results}\n"
        
        if entity_type == "company":
            synthesis_prompt = f"""You are a financial analyst. You just researched {entity_name} using web search. Synthesize the findings into a structured company profile.

SEARCH RESULTS:
{all_results}

Based ONLY on the search results above, create a comprehensive company profile with:

1. CURRENT VALUATION & FINANCIAL METRICS
   - Market cap / valuation (most recent)
   - Stock price (if public)
   - Revenue and growth rate
   - Margins and profitability
   - Any other financial metrics found

2. BUSINESS OVERVIEW
   - What the company does
   - Key products/services
   - Market position

3. COMPETITIVE ADVANTAGES
   - What makes them unique
   - Moats and defensibility

4. RECENT DEVELOPMENTS (2025-2026)
   - Latest news
   - Product launches
   - Strategic moves

5. GROWTH DRIVERS
   - What will drive future growth
   - Market opportunities

6. RISKS & CHALLENGES
   - Competition
   - Market risks
   - Execution challenges

7. VALUATION CONTEXT
   - How current valuation compares to peers
   - Whether stock/valuation seems high/low/fair
   - Key metrics for valuation

Format as a clear, factual summary based on the search results. If something wasn't found in search results, say "Not found in research". Use specific numbers when available.

BE FACTUAL - only include what was in the search results."""

        else:  # investor
            synthesis_prompt = f"""You are a financial analyst. You just researched {entity_name} using web search. Synthesize the findings into a structured investor profile.

SEARCH RESULTS:
{all_results}

Based ONLY on the search results above, create a comprehensive investor profile with:

1. FIRM OVERVIEW
   - AUM (assets under management)
   - Type of investor (VC, PE, asset manager, etc.)
   - Founded / history

2. INVESTMENT FOCUS
   - Sectors and stages they invest in
   - Geographic focus
   - Typical investment thesis

3. PORTFOLIO & TRACK RECORD
   - Notable investments
   - Recent deals
   - Success stories

4. INVESTMENT APPROACH
   - Typical check sizes
   - Investment criteria
   - Deal terms and structures

5. VALUE-ADD
   - What they bring beyond capital
   - Network, expertise, resources

6. NEGOTIATION STYLE
   - How they approach deals
   - What they prioritize
   - Red flags or requirements

Format as a clear, factual summary based on the search results. If something wasn't found in search results, say "Not found in research". Use specific numbers when available.

BE FACTUAL - only include what was in the search results."""

        try:
            print("[AI SYNTHESIS] Analyzing all research findings...")
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[types.Content(
                    role="user",
                    parts=[types.Part(text=synthesis_prompt)]
                )],
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    max_output_tokens=2000,
                )
            )
            
            synthesis = response.text.strip()
            print("[AI SYNTHESIS] ✓ Complete\n")
            
            return f"{entity_type.upper()}: {entity_name}\n\n{synthesis}"
            
        except Exception as e:
            print(f"[ERROR] AI synthesis failed: {e}")
            # Return raw results as fallback
            return f"{entity_type.upper()}: {entity_name}\n\n{all_results}"


# Global instance
_ai_fetcher = None

def get_ai_context_fetcher() -> AIContextFetcher:
    """Get or create AI context fetcher singleton"""
    global _ai_fetcher
    if _ai_fetcher is None:
        _ai_fetcher = AIContextFetcher()
    return _ai_fetcher