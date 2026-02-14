"""
Investor Agent
"""

from .base_agent import BaseAgent
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_investor_prompt, get_investor_context

class InvestorAgent(BaseAgent):
    """
    Institutional investor negotiation agent
    """
    
    def __init__(self, investor_name: str, websocket_url: str = "ws://localhost:9000"):
        """
        Initialize investor agent
        
        Args:
            investor_name: Name of investor (e.g., "BlackRock")
            websocket_url: WebSocket server URL
        """
        # Get investor context data
        context_data = get_investor_context(investor_name)
        
        # Build system prompt
        system_prompt = get_investor_prompt(investor_name, context_data)
        
        # Initialize base agent
        super().__init__(
            role="investor",
            name=investor_name,
            system_prompt=system_prompt,
            websocket_url=websocket_url
        )
        
        print(f"[INVESTOR AGENT] Representing {investor_name}")
        print(f"[PERSONALITY] Analytical, skeptical, data-focused")
        print(f"[OBJECTIVE] Risk-adjusted returns, portfolio discipline\n")