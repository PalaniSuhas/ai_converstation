"""
AI-Driven Company Agent
NO HARDCODING - Everything from AI reasoning + web search
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.base_agent_ai import BaseAgentAI
from utils.ai_context_fetcher import get_ai_context_fetcher
from utils.ai_prompts import get_company_ai_prompt


class AICompanyAgent(BaseAgentAI):
    """
    Fully AI-driven company/CEO negotiation agent
    - Research from web search (no hardcoded data)
    - Strategy from AI reasoning (no NLP rules)
    - Responses from AI generation (no templates)
    """
    
    def __init__(self, company_name: str, websocket_url: str = "ws://localhost:9000"):
        """
        Initialize AI-driven company agent
        
        Args:
            company_name: Name of company
            websocket_url: WebSocket server URL
        """
        print(f"\n{'='*60}")
        print(f"  INITIALIZING AI-DRIVEN COMPANY AGENT")
        print(f"{'='*60}")
        print(f"  Company: {company_name}")
        print(f"  Mode: FULLY AI (no hardcoding, no NLP)")
        print(f"{'='*60}\n")
        
        # Get AI context fetcher
        fetcher = get_ai_context_fetcher()
        
        # AI conducts research on the company
        print(f"[AI MODE] Researching {company_name} via web search...")
        print("[AI MODE] No hardcoded data - everything learned from web\n")
        
        # Use asyncio to run async context fetching
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ai_context = loop.run_until_complete(
            fetcher.get_company_context_ai(company_name)
        )
        loop.close()
        
        print(f"\n[AI RESEARCH] Context gathered ({len(ai_context)} characters)")
        print("[AI MODE] Agent will reason from this data\n")
        
        # Build AI prompt (no hardcoded strategy)
        system_prompt = get_company_ai_prompt(company_name, ai_context)
        
        # Initialize base AI agent
        super().__init__(
            role="company",
            name=company_name,
            system_prompt=system_prompt,
            websocket_url=websocket_url
        )
        
        print(f"[AI COMPANY AGENT] {company_name} ready")
        print(f"[AI MODE] Strategy: AI reasoning from research")
        print(f"[AI MODE] Responses: Generated dynamically")
        print(f"[OBJECTIVE] Maximize valuation via AI strategy\n")