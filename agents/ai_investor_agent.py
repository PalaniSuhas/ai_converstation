"""
AI-Driven Investor Agent
NO HARDCODING - Everything from AI reasoning + web search
FIXED: No event loop conflicts
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.base_agent_ai import BaseAgentAI
from utils.ai_context_fetcher import get_ai_context_fetcher
from utils.ai_prompts import get_investor_ai_prompt


class AIInvestorAgent(BaseAgentAI):
    """
    Fully AI-driven investor negotiation agent
    - Research from web search (no hardcoded data)
    - Strategy from AI reasoning (no NLP rules)
    - Responses from AI generation (no templates)
    """
    
    @classmethod
    async def create(cls, investor_name: str, websocket_url: str = "ws://localhost:9000"):
        """
        Async factory method to create AI-driven investor agent
        
        Args:
            investor_name: Name of investor
            websocket_url: WebSocket server URL
            
        Returns:
            Initialized AIInvestorAgent
        """
        print(f"\n{'='*60}")
        print(f"  INITIALIZING AI-DRIVEN INVESTOR AGENT")
        print(f"{'='*60}")
        print(f"  Investor: {investor_name}")
        print(f"  Mode: FULLY AI (no hardcoding, no NLP)")
        print(f"{'='*60}\n")
        
        # Get AI context fetcher
        fetcher = get_ai_context_fetcher()
        
        # AI conducts research on the investor
        print(f"[AI MODE] Researching {investor_name} via web search...")
        print("[AI MODE] No hardcoded data - everything learned from web\n")
        
        # Await the async research (no nested event loops!)
        ai_context = await fetcher.get_investor_context_ai(investor_name)
        
        print(f"\n[AI RESEARCH] Context gathered ({len(ai_context)} characters)")
        print("[AI MODE] Agent will reason from this data\n")
        
        # Build AI prompt (no hardcoded strategy)
        system_prompt = get_investor_ai_prompt(investor_name, ai_context)
        
        # Create instance
        instance = cls(investor_name, system_prompt, websocket_url)
        
        print(f"[AI INVESTOR AGENT] {investor_name} ready")
        print(f"[AI MODE] Strategy: AI reasoning from research")
        print(f"[AI MODE] Responses: Generated dynamically")
        print(f"[OBJECTIVE] Optimize returns via AI analysis\n")
        
        return instance
    
    def __init__(self, investor_name: str, system_prompt: str, websocket_url: str):
        """
        Internal initializer - use create() instead
        
        Args:
            investor_name: Investor name
            system_prompt: AI-generated system prompt
            websocket_url: WebSocket URL
        """
        # Initialize base AI agent
        super().__init__(
            role="investor",
            name=investor_name,
            system_prompt=system_prompt,
            websocket_url=websocket_url
        )