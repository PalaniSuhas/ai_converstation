"""
Company/CEO Agent
"""

from .base_agent import BaseAgent
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from utils import get_company_prompt, get_company_context

class CompanyAgent(BaseAgent):
    """
    Company/CEO negotiation agent
    """
    
    def __init__(self, company_name: str, websocket_url: str = "ws://localhost:9000"):
        """
        Initialize company agent
        
        Args:
            company_name: Name of company (e.g., "Tesla")
            websocket_url: WebSocket server URL
        """
        # Get company context data
        context_data = get_company_context(company_name)
        
        # Build system prompt
        system_prompt = get_company_prompt(company_name, context_data)
        
        # Initialize base agent
        super().__init__(
            role="company",
            name=company_name,
            system_prompt=system_prompt,
            websocket_url=websocket_url
        )
        
        print(f"[COMPANY AGENT] Representing {company_name}")
        print(f"[PERSONALITY] Confident, visionary, data-driven")
        print(f"[OBJECTIVE] Maximize valuation, minimize dilution\n")